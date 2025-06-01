import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  HStack,
  List,
  ListItem,
  Text,
  IconButton,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  Select, // For role selection
  Heading,
} from '@chakra-ui/react';
import { CloseIcon } from '@chakra-ui/icons';
// import { EventsService, UserPublic as ApiUserPublic, EventParticipantPublic as ApiEventParticipantPublic, /* EventParticipantCreate */ } from '../../client'; // Step 7
import {
    mockParticipants,
    addMockParticipant,
    removeMockParticipant,
    currentUserId, // To check against for permissions, e.g. can't remove self if creator
    mockUserAlice, // For mocking newly added user details
    mockUserBob,   // For mocking newly added user details
    mockUserCharlie // For mocking newly added user details
} from '../../mocks/mockData';

// Using existing placeholder interface, assuming structure is compatible
// Ensure UserPublic is defined if it's used for the 'user' field in EventParticipantPublic
export interface UserPublic { // Defined here if not imported from another component's def
    id: string;
    email: string;
    full_name?: string;
    is_active: boolean;
    is_superuser: boolean;
}
export interface EventParticipantPublic {
    user_id: string;
    event_id: string;
    role: string;
    added_at: string;
    user?: UserPublic;
}

// Matches the Pydantic model for the request body of add_event_participant endpoint
interface AddParticipantPayload {
    user_id_to_add: string;
    role: string;
}

interface EventParticipantManagerProps {
  eventId: string;
  // eventCreatorId?: string; // Optional: to implement specific creator permissions
}

const participantRoles = ["participant", "speaker", "organizer", "scribe", "admin", "bride", "groom", "officiant"];
// Mock user lookup - in real app, this might involve an API call to search users
const mockUserLookup: Record<string, UserPublic> = {
    [mockUserAlice.email]: mockUserAlice,
    [mockUserAlice.id]: mockUserAlice,
    [mockUserBob.email]: mockUserBob,
    [mockUserBob.id]: mockUserBob,
    [mockUserCharlie.email]: mockUserCharlie,
    [mockUserCharlie.id]: mockUserCharlie,
    "newuser@example.com": {id: "user-new-temp", email: "newuser@example.com", full_name: "New User", is_active: true, is_superuser: false}
};


const EventParticipantManager: React.FC<EventParticipantManagerProps> = ({ eventId }) => {
  const [participants, setParticipants] = useState<EventParticipantPublic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [userInput, setUserInput] = useState(''); // For user email or ID to add
  const [newUserRole, setNewUserRole] = useState(participantRoles[0]);
  const [isAdding, setIsAdding] = useState(false);
  // const { user: loggedInUser } = useAuth(); // For permission checks
  const loggedInUserId = currentUserId; // Using mock

  const toast = useToast();

  const fetchParticipants = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      console.log(`EventParticipantManager: Fetching participants for event ${eventId}`);
      await new Promise(resolve => setTimeout(resolve, 700));
      setParticipants(mockParticipants.filter(p => p.event_id === eventId));
    } catch (err) {
      console.error('Failed to fetch participants:', err);
      setError('Failed to load participants.');
    } finally {
      setIsLoading(false);
    }
  }, [eventId]);

  useEffect(() => {
    fetchParticipants();
  }, [fetchParticipants]);

  const handleAddParticipant = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || !newUserRole) {
        toast({ title: "User email/ID or role missing", status: "warning", duration: 3000, isClosable: true });
        return;
    }
    setIsAdding(true);

    // Simulate resolving email to user_id or using ID directly
    const userToAdd = mockUserLookup[userInput.toLowerCase()] || { id: userInput, email: userInput, full_name: `User ${userInput.substring(0,8)}`, is_active: true, is_superuser: false };

    if (participants.find(p => p.user_id === userToAdd.id)) {
        toast({ title: "Already Participant", description: `${userToAdd.full_name || userToAdd.email} is already in this event.`, status: "info" });
        setIsAdding(false);
        return;
    }

    const payload: AddParticipantPayload = { user_id_to_add: userToAdd.id, role: newUserRole };

    try {
      console.log("Adding participant (mock):", payload);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API

      const newParticipantEntry: EventParticipantPublic = {
          event_id: eventId,
          user_id: userToAdd.id,
          role: newUserRole,
          added_at: new Date().toISOString(),
          user: userToAdd
      };
      addMockParticipant(newParticipantEntry); // Add to global mock store
      fetchParticipants(); // Re-fetch to update local list

      toast({ title: 'Participant Added (Mock)', description: `${userToAdd.full_name || userToAdd.email} added as ${newUserRole}.`, status: 'success' });
      setUserInput('');
      setNewUserRole(participantRoles[0]);
    } catch (err) {
      console.error('Failed to add participant:', err);
      toast({ title: 'Failed to Add (Mock)', description: 'Could not add participant.', status: 'error' });
    } finally {
      setIsAdding(false);
    }
  };

  const handleRemoveParticipant = async (userIdToRemove: string) => {
    // Add permission check: e.g., only event creator or self-removal
    // const event = modifiableMockEvents.find(e => e.id === eventId);
    // if (loggedInUserId !== event?.creator_id && loggedInUserId !== userIdToRemove) {
    //    toast({ title: "Permission Denied", status: "error"}); return;
    // }
    if (!window.confirm(`Are you sure you want to remove participant ${mockUserLookup[userIdToRemove]?.full_name || userIdToRemove}?`)) return;

    try {
      console.log("Removing participant (mock):", userIdToRemove, "from event", eventId);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API

      removeMockParticipant(eventId, userIdToRemove); // Remove from global mock store
      fetchParticipants(); // Re-fetch to update local list

      toast({ title: 'Participant Removed (Mock)', description: `Participant removed.`, status: 'success' });
    } catch (err) {
      console.error('Failed to remove participant:', err);
      toast({ title: 'Failed to Remove (Mock)', description: 'Could not remove participant.', status: 'error' });
    }
  };

  if (isLoading) return <Spinner />;
  if (error) return <Alert status="error"><AlertIcon />{error}</Alert>;

  return (
    <Box>
      <Heading size="lg" mb={4}>Manage Participants</Heading>
      <VStack as="form" onSubmit={handleAddParticipant} spacing={4} mb={6} align="stretch">
        <FormControl id="user-input-to-add" isRequired>
          <FormLabel>User Email or ID to Add</FormLabel>
          <Input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Enter user's email or exact ID"
          />
        </FormControl>
        <FormControl id="user-role" isRequired>
          <FormLabel>Role</FormLabel>
          <Select value={newUserRole} onChange={(e) => setNewUserRole(e.target.value)}>
            {participantRoles.map(role => (
              <option key={role} value={role}>{role.charAt(0).toUpperCase() + role.slice(1)}</option>
            ))}
          </Select>
        </FormControl>
        <Button type="submit" colorScheme="blue" isLoading={isAdding} loadingText="Adding...">
          Add Participant
        </Button>
      </VStack>

      <Heading size="md" mb={3}>Current Participants</Heading>
      {participants.length === 0 ? (
        <Text>No participants yet.</Text>
      ) : (
        <List spacing={3}>
          {participants.map((p) => (
            <ListItem key={p.user_id} d="flex" justifyContent="space-between" alignItems="center" p={2} borderWidth="1px" borderRadius="md">
              <Box>
                <Text fontWeight="bold">{p.user?.full_name || p.user?.email || p.user_id}</Text>
                <Text fontSize="sm" color="gray.600">Role: {p.role}</Text>
              </Box>
              {/* Basic permission: Don't allow removing self if creator, or some other logic */}
              {/* This should be driven by current_user context eventually */}
              <IconButton
                aria-label="Remove participant"
                icon={<CloseIcon />}
                colorScheme="red"
                variant="ghost"
                onClick={() => handleRemoveParticipant(p.user_id)}
                // isDisabled={p.role === 'creator'} // Example: disable removing creator
              />
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
};

export default EventParticipantManager;
