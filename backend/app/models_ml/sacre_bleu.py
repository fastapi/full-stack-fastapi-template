from pydantic import BaseModel
import sacrebleu
import nltk # HLepor dependencies
# hlepor is vendored (see hlepor_vendored.py): the published package pulls
# nptyping, which is unmaintained and caps numpy <2.
from app.models_ml.hlepor_vendored import hlepor_score, single_hlepor_score
import os
import ctypes
import itertools
import Levenshtein

#lib_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib', 'libED.so')
# Resolved relative to this file: the uv workspace layout moves the app from
# /app/app to /app/backend/app, so an absolute path does not survive.
_lib_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib', 'libED.so')
ed_wrapper = ctypes.CDLL(_lib_path)
ed_wrapper.wrapper.restype = ctypes.c_float

# Define request and response models
class RequestInput(BaseModel):
    mt: str  # Source text
    ref: str   # Machine translation

class RequestOutput(BaseModel):
    mt: str
    ref: str
    score: float  # Single quality score

class RequestResponse(BaseModel):
    system_score: float  # Overall average score
    estimates: list[RequestOutput]

async def calculate_bleu(data: list[RequestInput]) -> RequestResponse:

    candidates = [item.mt.strip() for item in data]
    references = [[item.ref.strip() for item in data]]  # Ensure trimming whitespace

    # Calculate corpus BLEU score
    system_score = sacrebleu.corpus_bleu(candidates, references).score

    results = []
    for item in data:
        single_score = sacrebleu.sentence_bleu(item.mt, [item.ref]).score
        results.append(RequestOutput(mt=item.mt, ref=item.ref, score=single_score))

    return RequestResponse(system_score=system_score, estimates=results)

async def calculate_ter(data: list[RequestInput]) -> RequestResponse:

    candidates = [item.mt.strip() for item in data]
    references = [[item.ref.strip() for item in data]]  # Ensure trimming whitespace

    # Calculate corpus TER score
    system_score = sacrebleu.corpus_ter(candidates, references).score

    results = []
    for item in data:
        # Calculate individual TER scores using sacrebleu
        single_score = sacrebleu.sentence_ter(item.mt, [item.ref]).score
        results.append(RequestOutput(mt=item.mt, ref=item.ref, score=single_score))

    return RequestResponse(system_score=system_score, estimates=results)

async def calculate_chrf(data: list[RequestInput]) -> RequestResponse:

    candidates = [item.mt.strip() for item in data]
    references = [[item.ref.strip() for item in data]]  # Ensure trimming whitespace

    # Calculate corpus CHRF score
    system_score = sacrebleu.corpus_chrf(candidates, references).score

    results = []
    for item in data:
        # Calculate individual CHRF scores using sacrebleu
        single_score = sacrebleu.sentence_chrf(item.mt, [item.ref]).score
        results.append(RequestOutput(mt=item.mt, ref=item.ref, score=single_score))

    return RequestResponse(system_score=system_score, estimates=results)

async def calculate_hlepor(data: list[RequestInput]) -> RequestResponse:

    nltk.download('punkt') #for word_tokenize()
    nltk.download('punkt_tab') #for word_tokenize()
    candidates = [item.mt.strip() for item in data]
    references = [item.ref.strip() for item in data]  # Ensure trimming whitespace

    # Calculate corpus HLepor score
    system_score = hlepor_score(references, candidates)
    system_score = round(system_score, 4)

    results = []
    for item in data:
        # Calculate individual HLepor scores using sacrebleu
        single_score = single_hlepor_score(item.mt, item.ref)
        single_score = round(single_score, 4)
        results.append(RequestOutput(mt=item.mt, ref=item.ref, score=single_score))

    return RequestResponse(system_score=system_score, estimates=results)


class EditDistance:
    def __init__(self, ref, ed):
        self.dic = {}
        self.i = 0
        self.ed_wrapper = ed
        self.ref = self._word_to_num(ref)

    def __call__(self, hyp):
        return self._edit_distance(hyp)

    def _edit_distance(self, hyp):
        hyp_c = (ctypes.c_ulonglong * len(hyp))()
        ref_c = (ctypes.c_ulonglong * len(self.ref))()
        hyp_c[:] = self._word_to_num(hyp)
        ref_c[:] = self.ref
        norm = len(ref_c)
        result = self.ed_wrapper.wrapper(hyp_c, ref_c, len(hyp_c), len(ref_c), norm)
        return result

    def _word_to_num(self, words):
        res = []
        for word in words:
            if word in self.dic:
                res.append(self.dic[word])
            else:
                self.dic[word] = self.i
                res.append(self.i)
                self.i += 1
        return res


def _shift_cost(shifted_words, original_words):
    shift_cost = 0
    original_start = 0
    while original_start < len(shifted_words):
        avg_shifted_characters = 0
        original_index = original_start
        if original_words[original_start] == shifted_words[original_start]:
            original_start += 1
            continue
        for shift_start in range(original_start + 1, len(shifted_words)):
            if original_words[original_start] == shifted_words[shift_start]:
                length = 1
                for pos in range(1, len(original_words) - original_index):
                    if shift_start + pos < len(shifted_words) and original_words[original_index + pos] == shifted_words[shift_start + pos]:
                        length += 1
                        if original_start + 1 < len(original_words):
                            original_start += 1
                    else:
                        break
                shifted_characters = sum(len(original_words[original_index + i]) for i in range(length))
                avg_shifted_characters = shifted_characters / length
                break
        shift_cost += avg_shifted_characters
        original_start += 1
    return shift_cost


def couple_discoverer(sentence_1, sentence_2):
    for start_1, start_2 in itertools.product(range(len(sentence_1)), range(len(sentence_2))):
        if start_1 == start_2:
            continue
        if sentence_1[start_1] == sentence_2[start_2]:
            length = 1
            for step in range(1, len(sentence_1) - start_1):
                end_1, end_2 = start_1 + step, start_2 + step
                if end_2 < len(sentence_2) and sentence_1[end_1] == sentence_2[end_2]:
                    length += 1
                else:
                    break
            yield (start_1, start_2, length)


def shifter(hyp_words, ref_words, pre_score, edit_distance):
    scores = []
    for hyp_start, ref_start, length in couple_discoverer(hyp_words, ref_words):
        shifted_words = hyp_words[:hyp_start] + hyp_words[hyp_start + length:]
        shifted_words[ref_start:ref_start] = hyp_words[hyp_start:hyp_start + length]
        scores.append((pre_score - edit_distance(shifted_words), shifted_words))
    if not scores:
        return 0, hyp_words
    scores.sort()
    return scores[-1]


def cer(hyp_words, ref_words, ed_wrapper):
    hyp_backup = hyp_words[:]
    edit_distance = EditDistance(ref_words, ed_wrapper)
    pre_score = edit_distance(hyp_words)
    if pre_score == 0:
        return 0.0
    while True:
        diff, new_words = shifter(hyp_words, ref_words, pre_score, edit_distance)
        if diff <= 0:
            break
        hyp_words = new_words
        pre_score -= diff
    shift_cost = _shift_cost(hyp_words, hyp_backup)
    shifted_chars = " ".join(hyp_words)
    ref_chars = " ".join(ref_words)
    if len(shifted_chars) == 0:
        return 1.0
    edit_cost = Levenshtein.distance(shifted_chars, ref_chars) + shift_cost
    return min(1.0, edit_cost / len(shifted_chars))


async def calculate_character(data: list[RequestInput]) -> RequestResponse:
    results = []
    scores = []
    for item in data:
        mt_words = item.mt.strip().split()
        ref_words = item.ref.strip().split()
        score = cer(mt_words, ref_words, ed_wrapper)
        score = round(score, 4) * 100 
        results.append(RequestOutput(mt=item.mt, ref=item.ref, score=score))
        scores.append(score)
    system_score = round(sum(scores) / len(scores), 4) if scores else 0.0
    return RequestResponse(system_score=system_score, estimates=results)