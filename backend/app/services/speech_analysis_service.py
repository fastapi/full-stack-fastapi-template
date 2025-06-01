import uuid
from typing import List, Dict, Any, Optional
from collections import Counter
from dataclasses import dataclass, field # Using dataclass for internal model

from sqlmodel import Session
from app import crud, models

# Internal representation of a nudge
@dataclass
class PersonalizedNudge:
    user_id: uuid.UUID  # For whom the nudge is intended
    nudge_type: str     # e.g., "tone_mismatch", "keyword_overlap", "length_discrepancy"
    message: str        # The actual advice
    severity: str       # e.g., "info", "warning", "suggestion"
    related_speech_ids: List[uuid.UUID] = field(default_factory=list) # Optional: to link nudge to specific speeches


# Simplified speech data for analysis
@dataclass
class SpeechData:
    speech_id: uuid.UUID
    creator_id: uuid.UUID
    draft: str
    tone: str
    duration: int
    version_id: uuid.UUID


# Basic stopwords (extend as needed)
STOPWORDS = set([
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "should",
    "can", "could", "may", "might", "must", "and", "but", "or", "nor",
    "for", "so", "yet", "in", "on", "at", "by", "from", "to", "with",
    "about", "above", "after", "again", "against", "all", "am", "as",
    "at", "because", "before", "below", "between", "both", "but", "by",
    "can't", "cannot", "could've", "couldn't", "didn't", "doesn't",
    "don't", "down", "during", "each", "few", "further", "hadn't",
    "hasn't", "haven't", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "into", "it", "it's", "its",
    "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "not", "of", "off", "once", "only", "other", "ought", "our",
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should've", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd",
    "they'll", "they're", "they've", "this", "those", "through", "too",
    "under", "until", "up", "very", "wasn't", "we", "we'd", "we'll",
    "we're", "we've", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why",
    "why's", "won't", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves", "it.", "this."
])

def basic_extract_keywords(text: str, num_keywords: int = 5) -> List[str]:
    words = [word.lower().strip(".,!?;:'\"()") for word in text.split()]
    filtered_words = [word for word in words if word and word not in STOPWORDS and len(word)>2]
    if not filtered_words:
        return []
    word_counts = Counter(filtered_words)
    return [word for word, count in word_counts.most_common(num_keywords)]

def analyse_event_speeches(db: Session, event_id: uuid.UUID) -> List[PersonalizedNudge]:
    all_nudges: List[PersonalizedNudge] = []

    event_speeches = crud.get_event_speeches(session=db, event_id=event_id)
    if not event_speeches or len(event_speeches) < 1: # Need at least 1 speech for some analysis, 2 for comparison
        return []

    speech_data_list: List[SpeechData] = []
    for speech in event_speeches:
        if speech.current_version_id:
            version = crud.get_speech_version(session=db, version_id=speech.current_version_id)
            if version and version.speech_draft: # Ensure there is a draft to analyze
                speech_data_list.append(
                    SpeechData(
                        speech_id=speech.id,
                        creator_id=speech.creator_id,
                        draft=version.speech_draft,
                        tone=version.speech_tone,
                        duration=version.estimated_duration_minutes,
                        version_id=version.id
                    )
                )
        else:
            # Nudge for speeches without a current version or draft
            all_nudges.append(PersonalizedNudge(
                user_id=speech.creator_id,
                nudge_type="missing_draft",
                message=f"Your speech '{crud.get_speech(session=db, speech_id=speech.id).event_name if hasattr(crud.get_speech(session=db, speech_id=speech.id), 'event_name') else 'Unnamed Speech'}' doesn't have a current version with a draft. Add a draft to include it in the analysis.",
                severity="warning",
                related_speech_ids=[speech.id]
            ))

    if len(speech_data_list) < 2: # Most comparisons need at least two speeches with drafts
        # Add nudges if only one speech has a draft? For now, returning early.
        return all_nudges


    # --- Perform Comparisons (Iterating through pairs) ---
    for i in range(len(speech_data_list)):
        for j in range(i + 1, len(speech_data_list)):
            s1 = speech_data_list[i]
            s2 = speech_data_list[j]

            # 1. Tone Comparison
            if s1.tone.lower() != s2.tone.lower():
                msg1 = f"Your speech tone ('{s1.tone}') differs from another participant's ('{s2.tone}'). Consider if this contrast is intentional and how it contributes to the event's flow."
                all_nudges.append(PersonalizedNudge(s1.creator_id, "tone_mismatch", msg1, "suggestion", [s1.speech_id, s2.speech_id]))
                msg2 = f"Your speech tone ('{s2.tone}') differs from another participant's ('{s1.tone}'). Consider if this contrast is intentional and how it contributes to the event's flow."
                all_nudges.append(PersonalizedNudge(s2.creator_id, "tone_mismatch", msg2, "suggestion", [s1.speech_id, s2.speech_id]))

            # 2. Length Comparison (e.g., if difference > 50% of shorter speech, or a fixed threshold)
            shorter = min(s1.duration, s2.duration)
            longer = max(s1.duration, s2.duration)
            if longer > shorter * 1.5 and longer - shorter > 3: # Difference of at least 50% and 3 mins
                msg_s1 = f"Your speech is {s1.duration} mins. Another participant's speech is {s2.duration} mins. You might want to coordinate lengths for better event balance."
                all_nudges.append(PersonalizedNudge(s1.creator_id, "length_discrepancy", msg_s1, "suggestion", [s1.speech_id, s2.speech_id]))
                msg_s2 = f"Your speech is {s2.duration} mins. Another participant's speech is {s1.duration} mins. You might want to coordinate lengths for better event balance."
                all_nudges.append(PersonalizedNudge(s2.creator_id, "length_discrepancy", msg_s2, "suggestion", [s1.speech_id, s2.speech_id]))

            # 3. Basic Keyword Overlap
            keywords1 = basic_extract_keywords(s1.draft, num_keywords=5) # Using the utility
            keywords2 = basic_extract_keywords(s2.draft, num_keywords=5) # Using the utility

            common_keywords = set(keywords1) & set(keywords2)
            if len(common_keywords) >= 1: # If at least 1 common important keyword
                kw_str = ", ".join(list(common_keywords)[:3]) # Show up to 3
                msg1 = f"You and another participant both seem to touch on themes like '{kw_str}'. This could be a good link, or ensure you're bringing unique perspectives."
                all_nudges.append(PersonalizedNudge(s1.creator_id, "keyword_overlap", msg1, "info", [s1.speech_id, s2.speech_id]))
                msg2 = f"You and another participant both seem to touch on themes like '{kw_str}'. This could be a good link, or ensure you're bringing unique perspectives."
                all_nudges.append(PersonalizedNudge(s2.creator_id, "keyword_overlap", msg2, "info", [s1.speech_id, s2.speech_id]))

    return all_nudges
