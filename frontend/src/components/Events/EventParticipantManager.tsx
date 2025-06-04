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
import React, { useState, useCallback } from 'react'; // Removed useEffect
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
  Select,
  Heading,
  AlertDescription,
  AlertTitle,
} from '@chakra-ui/react';
import { CloseIcon } from '@chakra-ui/icons';
import { EventsService, UserPublic, EventParticipantPublic, Body_events_add_event_participant, ApiError, Message } from '../../../client';
// import { useAuth } from '../../../hooks/useAuth'; // For currentUserId

interface EventParticipantManagerProps {
  eventId: string;
  // eventCreatorId?: string; // Optional for more granular permissions
}

// Note: The UserPublic type from the client might not include all fields if they are from a separate endpoint.
// The listEventParticipants endpoint returns Array<UserPublic>.
// We'll assume UserPublic from client has what we need (id, email, full_name).

const participantRoles = ["participant", "speaker", "organizer", "scribe", "admin", "bride", "groom", "officiant"];

const EventParticipantManager: React.FC<EventParticipantManagerProps> = ({ eventId }) => {
  const queryClient = useQueryClient();
  const toast = useToast();
  // const { user: loggedInUser } = useAuth();
  // const currentUserId = loggedInUser?.id;

  const [userInput, setUserInput] = useState(''); // For user email or ID to add
  const [newUserRole, setNewUserRole] = useState(participantRoles[0]);

  const {
    data: participants,
    isLoading: isLoadingParticipants,
    isError: isParticipantsError,
    error: participantsError
  } = useQuery<UserPublic[], ApiError>({ // API returns Array<UserPublic>
    queryKey: ['eventParticipants', eventId],
    queryFn: async () => EventsService.listEventParticipants({ eventId }),
    enabled: !!eventId,
  });

  const addParticipantMutation = useMutation<
    EventParticipantPublic, // Response type from addEventParticipant
    ApiError,
    Body_events_add_event_participant // Request body type
  >({
    mutationFn: async (participantData: Body_events_add_event_participant) => {
      return EventsService.addEventParticipant({ eventId, requestBody: participantData });
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['eventParticipants', eventId] });
      toast({
        title: 'Participant Added',
        description: `User has been added as ${data.role}.`,
        status: 'success',
        duration: 3000,
        isClosable: true,
    });
      setUserInput('');
      setNewUserRole(participantRoles[0]);
    },
    onError: (error) => {
      toast({
        title: 'Failed to Add Participant',
        description: error.body?.detail || error.message || 'Could not add participant.',
        status: 'error',
        duration: 5000,
        isClosable: true,
    });
    },
  });

  const removeParticipantMutation = useMutation<
    Message, // Response type from removeEventParticipant
    ApiError,
    { userIdToRemove: string } // Variables for mutationFn
  >({
    mutationFn: async ({ userIdToRemove }) => {
      return EventsService.removeEventParticipant({ eventId, userIdToRemove });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['eventParticipants', eventId] });
      toast({ title: 'Participant Removed', status: 'success', duration: 3000, isClosable: true });
    },
    onError: (error) => {
      toast({
        title: 'Failed to Remove Participant',
        description: error.body?.detail || error.message || 'Could not remove participant.',
        status: 'error',
        duration: 5000,
        isClosable: true,
    });
    },
  });

  const handleAddParticipantSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || !newUserRole) {
      toast({ title: "User ID/Email and role are required.", status: "warning", duration: 3000, isClosable: true });
      return;
    }
    // Assuming userInput is the user_id (UUID string) as per backend expectation for `user_id_to_add`
    // In a real app, might need a lookup from email to ID if backend doesn't handle email directly.
    addParticipantMutation.mutate({ user_id_to_add: userInput, role: newUserRole });
  };

  const handleRemoveParticipantClick = (userIdToRemove: string) => {
    // Add more robust confirmation if desired
    if (window.confirm(`Are you sure you want to remove this participant?`)) {
      removeParticipantMutation.mutate({ userIdToRemove });
    }
  };

  if (isLoadingParticipants) return (
    <Box textAlign="center" p={5}><Spinner size="lg" /><Text mt={2}>Loading participants...</Text></Box>
  );

  if (isParticipantsError) return (
    <Alert status="error" mt={4}>
      <AlertIcon />
      <AlertTitle>Error Loading Participants</AlertTitle>
      <AlertDescription>{participantsError?.body?.detail || participantsError?.message || 'An unexpected error occurred.'}</AlertDescription>
    </Alert>
  );

  return (
    <Box>
      <Heading size="lg" mb={4}>Manage Participants</Heading>
      <VStack as="form" onSubmit={handleAddParticipantSubmit} spacing={4} mb={6} align="stretch">
        <FormControl id="user-id-to-add" isRequired isInvalid={!!addParticipantMutation.error?.body?.detail?.find((err: any) => err.loc?.includes('user_id_to_add'))}>
          <FormLabel>User ID to Add</FormLabel>
          <Input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Enter exact User ID (UUID)"
            isDisabled={addParticipantMutation.isPending}
          />
        </FormControl>
        <FormControl id="user-role" isRequired isInvalid={!!addParticipantMutation.error?.body?.detail?.find((err: any) => err.loc?.includes('role'))}>
          <FormLabel>Role</FormLabel>
          <Select
            value={newUserRole}
            onChange={(e) => setNewUserRole(e.target.value)}
            isDisabled={addParticipantMutation.isPending}
          >
            {participantRoles.map(role => (
              <option key={role} value={role}>{role.charAt(0).toUpperCase() + role.slice(1)}</option>
            ))}
          </Select>
        </FormControl>
        <Button type="submit" colorScheme="blue" isLoading={addParticipantMutation.isPending} loadingText="Adding...">
          Add Participant
        </Button>
      </VStack>

      <Heading size="md" mb={3}>Current Participants</Heading>
      {!participants || participants.length === 0 ? (
        <Text>No participants yet.</Text>
      ) : (
        <List spacing={3}>
          {participants.map((participant) => (
            <ListItem key={participant.id} d="flex" justifyContent="space-between" alignItems="center" p={2} borderWidth="1px" borderRadius="md">
              <Box>
                {/* Assuming UserPublic has full_name and email. Adjust if structure differs. */}
                <Text fontWeight="bold">{participant.full_name || participant.email || participant.id}</Text>
                {/* The API for listEventParticipants returns UserPublic, which doesn't include 'role'.
                    This means we can't display role directly from this list.
                    This is a mismatch between `EventParticipantPublic` (which has role) and `UserPublic`.
                    The backend `GET /events/{event_id}/participants` returns `list[UserPublic]`.
                    To show role, backend would need to return `list[EventParticipantPublic]` or similar.
                    For now, role cannot be displayed here from the API call.
                    If we want to keep showing role as in mock, we'd need to adjust backend response or make another call.
                */}
                {/* <Text fontSize="sm" color="gray.600">Role: {participant.role}</Text> */}
              </Box>
              <IconButton
                aria-label="Remove participant"
                icon={<CloseIcon />}
                colorScheme="red"
                variant="ghost"
                onClick={() => handleRemoveParticipantClick(participant.id)} // participant.id is user_id here
                isLoading={removeParticipantMutation.isPending && removeParticipantMutation.variables?.userIdToRemove === participant.id}
                // Example permission: isDisabled={participant.id === currentUserId && event?.creator_id === currentUserId}
              />
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
};

export default EventParticipantManager;
