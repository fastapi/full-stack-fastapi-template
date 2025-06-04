import { CoordinationEventPublic } from '../components/Events/EventListItem';
import { EventParticipantPublic } from '../components/Events/EventParticipantManager'; // Assuming UserPublic is nested or handled
import { SecretSpeechPublic } from '../components/Speeches/SpeechListItem';
import { SecretSpeechVersionHistoryItem } from '../components/Speeches/SpeechVersionHistory';
import { PersonalizedNudgePublic } from '../components/Analysis/SpeechAnalysisDisplay';
import { SecretSpeechPublicDetailed, SecretSpeechVersionData } from '../components/Speeches/SpeechDetailPage';


export const currentUserId = 'user-123-alice'; // Alice - our main user

// --- Users (for creator references) ---
export const mockUserAlice = { id: currentUserId, email: 'alice@example.com', full_name: 'Alice Wonderland', is_active: true, is_superuser: false };
export const mockUserBob = { id: 'user-456-bob', email: 'bob@example.com', full_name: 'Bob The Builder', is_active: true, is_superuser: false };
export const mockUserCharlie = { id: 'user-789-charlie', email: 'charlie@example.com', full_name: 'Charlie Brown', is_active: true, is_superuser: false };


// --- Coordination Events ---
export const mockEvents: CoordinationEventPublic[] = [
  {
    id: 'event-001-wedding',
    event_name: "Alice & Bob's Wedding Ceremony",
    event_type: 'wedding_ceremony',
    event_date: new Date(2024, 10, 15, 14, 0, 0).toISOString(), // Nov 15, 2024
    creator_id: mockUserAlice.id,
    created_at: new Date(Date.now() - 86400000 * 10).toISOString(),
    updated_at: new Date(Date.now() - 86400000 * 2).toISOString(),
  },
  {
    id: 'event-002-techconf',
    event_name: 'Tech Conference 2024 - Keynotes',
    event_type: 'conference_keynotes',
    event_date: new Date(2024, 8, 20, 9, 0, 0).toISOString(), // Sep 20, 2024
    creator_id: mockUserBob.id,
    created_at: new Date(Date.now() - 86400000 * 20).toISOString(),
    updated_at: new Date(Date.now() - 86400000 * 5).toISOString(),
  },
  {
    id: 'event-003-bookclub',
    event_name: "Book Club - Monthly Discussion",
    event_type: 'book_club_meeting',
    // No event_date (recurring or TBD)
    creator_id: mockUserAlice.id,
    created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
    updated_at: new Date(Date.now() - 86400000 * 1).toISOString(),
  },
];

// --- Event Participants ---
export let mockParticipants: EventParticipantPublic[] = [
  // Event 1: Wedding
  { event_id: 'event-001-wedding', user_id: mockUserAlice.id, role: 'bride', added_at: new Date().toISOString(), user: mockUserAlice },
  { event_id: 'event-001-wedding', user_id: mockUserBob.id, role: 'groom', added_at: new Date().toISOString(), user: mockUserBob },
  { event_id: 'event-001-wedding', user_id: mockUserCharlie.id, role: 'officiant', added_at: new Date().toISOString(), user: mockUserCharlie },
  // Event 2: Tech Conference
  { event_id: 'event-002-techconf', user_id: mockUserBob.id, role: 'organizer', added_at: new Date().toISOString(), user: mockUserBob },
  { event_id: 'event-002-techconf', user_id: mockUserAlice.id, role: 'speaker', added_at: new Date().toISOString(), user: mockUserAlice },
  // Event 3: Book Club - initially only Alice
  { event_id: 'event-003-bookclub', user_id: mockUserAlice.id, role: 'host', added_at: new Date().toISOString(), user: mockUserAlice },
];

// --- Secret Speeches & Versions ---
// Helper to create version data
const createVersion = (id: string, num: number, speech_id: string, creator_id: string, tone: string, duration: number, draft: string, daysAgo: number): SecretSpeechVersionData => ({
  id,
  version_number: num,
  speech_id, // Not strictly needed in SecretSpeechVersionData but good for consistency
  creator_id,
  speech_tone: tone,
  estimated_duration_minutes: duration,
  speech_draft: draft,
  created_at: new Date(Date.now() - 86400000 * daysAgo).toISOString(),
});

export let mockSpeechVersionsStore: Record<string, SecretSpeechVersionHistoryItem[]> = {
  'speech-a1-vows': [
    createVersion('v-a1-1', 1, 'speech-a1-vows', mockUserAlice.id, 'sentimental', 3, "My dearest Bob, version 1...", 5),
    createVersion('v-a1-2', 2, 'speech-a1-vows', mockUserAlice.id, 'heartfelt', 4, "My dearest Bob, I can't wait... version 2.", 2),
    createVersion('v-a1-3', 3, 'speech-a1-vows', mockUserAlice.id, 'loving', 3, "My dearest Bob, my love for you... final version.", 1),
  ],
  'speech-b1-vows': [
    createVersion('v-b1-1', 1, 'speech-b1-vows', mockUserBob.id, 'romantic', 3, "My beloved Alice, version 1...", 4),
    createVersion('v-b1-2', 2, 'speech-b1-vows', mockUserBob.id, 'passionate', 3, "My beloved Alice, my heart beats... final version.", 1),
  ],
  'speech-a2-keynote': [
    createVersion('v-a2-1', 1, 'speech-a2-keynote', mockUserAlice.id, 'informative', 20, "Tech trends in 2024, first draft.", 7),
    createVersion('v-a2-2', 2, 'speech-a2-keynote', mockUserAlice.id, 'engaging', 25, "Tech trends, more examples, second draft.", 3),
  ],
  'speech-b2-opening': [
     createVersion('v-b2-1', 1, 'speech-b2-opening', mockUserBob.id, 'welcoming', 5, "Welcome to TechConf 2024!", 2),
  ]
};

export let mockSpeeches: SecretSpeechPublicDetailed[] = [
  // Event 1: Wedding
  {
    id: 'speech-a1-vows',
    event_id: 'event-001-wedding',
    creator_id: mockUserAlice.id,
    creator_name: mockUserAlice.full_name,
    created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
    updated_at: new Date(Date.now() - 86400000 * 1).toISOString(),
    current_version_id: 'v-a1-3',
    current_version: mockSpeechVersionsStore['speech-a1-vows'][2],
  },
  {
    id: 'speech-b1-vows',
    event_id: 'event-001-wedding',
    creator_id: mockUserBob.id,
    creator_name: mockUserBob.full_name,
    created_at: new Date(Date.now() - 86400000 * 4).toISOString(),
    updated_at: new Date(Date.now() - 86400000 * 1).toISOString(),
    current_version_id: 'v-b1-2',
    current_version: mockSpeechVersionsStore['speech-b1-vows'][1],
  },
  // Event 2: Tech Conference
  {
    id: 'speech-a2-keynote',
    event_id: 'event-002-techconf',
    creator_id: mockUserAlice.id,
    creator_name: mockUserAlice.full_name,
    created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
    updated_at: new Date(Date.now() - 86400000 * 3).toISOString(),
    current_version_id: 'v-a2-2',
    current_version: mockSpeechVersionsStore['speech-a2-keynote'][1],
  },
   {
    id: 'speech-b2-opening',
    event_id: 'event-002-techconf',
    creator_id: mockUserBob.id,
    creator_name: mockUserBob.full_name,
    created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
    updated_at: new Date(Date.now() - 86400000 * 2).toISOString(),
    current_version_id: 'v-b2-1',
    current_version: mockSpeechVersionsStore['speech-b2-opening'][0],
  },
  // Event 3: Book Club (initially no speeches)
];


// --- Personalized Nudges ---
export const mockNudges: PersonalizedNudgePublic[] = [
  {
    nudge_type: 'tone_consistency_event',
    message: "Some speeches in this event have a 'humorous' tone, while others are 'serious'. Ensure this is the intended dynamic for the overall event flow.",
    severity: 'info',
  },
  {
    nudge_type: 'length_variation_user',
    message: "Your speech 'Alice's Vows' is 3 minutes, which is a bit shorter than other vow speeches (around 4-5 minutes). This is fine, but you could elaborate more if desired.",
    severity: 'suggestion',
  },
  {
    nudge_type: 'keyword_focus_speech',
    message: "Your keynote speech heavily focuses on 'AI innovation'. Consider briefly touching upon 'ethical implications' for a more rounded perspective if time allows.",
    severity: 'suggestion',
  },
   {
    nudge_type: 'missing_speech_for_participant',
    message: "You are listed as a 'speaker' for the Tech Conference but haven't added a speech yet. Remember to add your speech details!",
    severity: 'warning',
  }
];

// Functions to manipulate mock data (simulating CRUD operations)
export const addMockParticipant = (participant: EventParticipantPublic) => {
  mockParticipants.push(participant);
};

export const removeMockParticipant = (eventId: string, userId: string) => {
  mockParticipants = mockParticipants.filter(p => !(p.event_id === eventId && p.user_id === userId));
};

export const addMockSpeech = (speech: SecretSpeechPublicDetailed) => {
  mockSpeeches.push(speech);
  if (speech.current_version) { // Add its first version to the store
    if (!mockSpeechVersionsStore[speech.id]) {
      mockSpeechVersionsStore[speech.id] = [];
    }
    mockSpeechVersionsStore[speech.id].push({
        ...speech.current_version,
        speech_id: speech.id, // ensure speech_id is set
    });
  }
};

export const addMockSpeechVersion = (speechId: string, version: SecretSpeechVersionData) => {
    if (!mockSpeechVersionsStore[speechId]) {
        mockSpeechVersionsStore[speechId] = [];
    }
    mockSpeechVersionsStore[speechId].push({...version, speech_id: speechId}); // ensure speech_id
    // Update the main speech's current_version
    const speechIndex = mockSpeeches.findIndex(s => s.id === speechId);
    if (speechIndex !== -1) {
        mockSpeeches[speechIndex].current_version_id = version.id;
        mockSpeeches[speechIndex].current_version = version;
        mockSpeeches[speechIndex].updated_at = new Date().toISOString();
    }
};

export const setMockSpeechCurrentVersion = (speechId: string, versionId: string) => {
    const speechIndex = mockSpeeches.findIndex(s => s.id === speechId);
    const versions = mockSpeechVersionsStore[speechId];
    if (speechIndex !== -1 && versions) {
        const newCurrentVersion = versions.find(v => v.id === versionId);
        if (newCurrentVersion) {
            mockSpeeches[speechIndex].current_version_id = newCurrentVersion.id;
            mockSpeeches[speechIndex].current_version = newCurrentVersion;
            mockSpeeches[speechIndex].updated_at = new Date().toISOString();
        }
    }
};

console.log("Mock data initialized with currentUserId:", currentUserId);
console.log("Alice's ID:", mockUserAlice.id);
console.log("Bob's ID:", mockUserBob.id);

// To ensure we can add to mockEvents for EventCreateForm simulation
export let modifiableMockEvents = [...mockEvents];
export const addMockEvent = (event: CoordinationEventPublic) => {
  modifiableMockEvents.push(event);
};

// Ensure all exports are correctly picked up
// (No specific action needed here, just a comment for clarity)
// The mock data structures are now defined.
// Next step will be to update components.
// Note: For EventParticipantPublic, `user` details are directly embedded.
// For SecretSpeechPublic (used in SpeechListItem), `creator_name` and current version details are denormalized.
// For SecretSpeechPublicDetailed (used in SpeechDetailPage), `current_version` is a nested object.
// This aligns with typical needs for list vs. detail views.
// `mockSpeechVersionsStore` stores all versions for all speeches.
// The main `mockSpeeches` array holds the speech itself and only its *current* version.
// Helper functions are provided to simulate backend operations by modifying these mock arrays/objects.
// The `currentUserId` is 'user-123-alice', so Alice is our primary test user.
// Speeches created by Alice should allow her to see drafts and edit.
// Speeches by Bob, when viewed by Alice, should hide drafts.
// Event 'event-001-wedding' has speeches from both Alice and Bob.
// Event 'event-002-techconf' also has speeches from Alice and Bob.
// Event 'event-003-bookclub' is created by Alice and initially has no speeches.
// Participant roles are varied.
// Nudges are generic for now and will be returned for any analysis request.
// Added `modifiableMockEvents` for `EventCreateForm` to simulate adding to the list seen by `EventList`.
// Added console logs for user IDs to help with debugging during component updates.Okay, the `frontend/src/mocks/mockData.ts` file has been created with detailed mock data for events, participants, speeches (including versions), and nudges. It also includes a `currentUserId` (`user-123-alice`) and helper functions to simulate CRUD operations on the mock data.

**Key aspects of the mock data:**
*   `currentUserId` is set to Alice's ID.
*   `mockEvents`: Includes events created by Alice and Bob, with one event having no date.
*   `mockParticipants`: Alice, Bob, and Charlie participate in events with different roles.
*   `mockSpeeches` & `mockSpeechVersionsStore`:
    *   Alice has speeches where she is the creator (e.g., `speech-a1-vows`, `speech-a2-keynote`).
    *   Bob also has speeches (e.g., `speech-b1-vows`, `speech-b2-opening`).
    *   Drafts are included in `mockSpeechVersionsStore`. `mockSpeeches` contains the detailed `current_version` object.
*   `mockNudges`: A set of generic nudges.
*   Helper functions like `addMockSpeech`, `addMockSpeechVersion`, `setMockSpeechCurrentVersion`, `addMockParticipant`, `removeMockParticipant`, `addMockEvent` are defined to simulate backend updates.
*   `modifiableMockEvents` is an export to allow `EventCreateForm` to simulate adding to the list `EventList` uses.

**Step 2: Update Components to Use Mock Data**

Now, I'll go through each component and modify it to use this mock data.

**2.1. `EventList.tsx`**
