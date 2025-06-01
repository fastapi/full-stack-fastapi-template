import React, { useState } from 'react';
import {
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  useToast,
  Select, // For event_type dropdown
} from '@chakra-ui/react';
// import { EventsService, CoordinationEventCreate as ApiCoordinationEventCreate } from '../../client'; // Step 7
// import { useAuth } from '../../hooks/useAuth'; // If needed for user context
import { addMockEvent, currentUserId, mockUserAlice } from '../../mocks/mockData'; // Import mock function and user
import { CoordinationEventPublic } from './EventListItem'; // To shape the object for mock list

// Temporary interface until client is fully integrated (matches backend Pydantic model)
interface CoordinationEventCreatePayload {
  event_name: string;
  event_type: string;
  event_date?: string; // ISO string format for date
}

// Predefined event types - can be expanded
const eventTypes = [
  { value: "wedding_speech_pair", label: "Wedding Speech Pair" },
  { value: "vows_exchange", label: "Vows Exchange" },
  { value: "team_presentation", label: "Team Presentation" },
  { value: "debate_session", label: "Debate Session" },
  { value: "other", label: "Other" },
];

const EventCreateForm: React.FC = () => {
  const [eventName, setEventName] = useState('');
  const [eventType, setEventType] = useState(eventTypes[0].value); // Default to first type
  const [eventDate, setEventDate] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();
  // const { user } = useAuth();
  // const actualCreatorId = user?.id || currentUserId; // Use logged-in user or fallback to mock
  const actualCreatorId = currentUserId; // Using mock currentUserId

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    if (!eventName.trim() || !eventType) {
        toast({
            title: 'Missing fields',
            description: 'Event Name and Type are required.',
            status: 'error',
            duration: 5000,
            isClosable: true,
        });
        setIsLoading(false);
        return;
    }

    const payload: CoordinationEventCreatePayload = {
      event_name: eventName,
      event_type: eventType,
      ...(eventDate && { event_date: new Date(eventDate).toISOString() }),
    };

    try {
      console.log('Submitting event data to mock:', payload);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Create a full CoordinationEventPublic object for the mock list
      const newMockEvent: CoordinationEventPublic = {
        id: `event-mock-${Date.now()}`, // Simple unique ID for mock
        ...payload,
        creator_id: actualCreatorId,
        // creator_name: mockUserAlice.full_name, // Assuming Alice is creating
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      addMockEvent(newMockEvent); // Add to the shared mock data array

      toast({
        title: 'Event Created (Mock)',
        description: `${newMockEvent.event_name} has been successfully created.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      setEventName('');
      setEventType(eventTypes[0].value);
      setEventDate('');
      // Potentially redirect or update a list of events
    } catch (error) {
      console.error('Failed to create event:', error);
      toast({
        title: 'Creation Failed',
        description: 'There was an error creating the event. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <VStack spacing={4} as="form" onSubmit={handleSubmit} w="100%" maxW="md" m="auto">
      <Heading as="h2" size="lg" textAlign="center">
        Create New Coordination Event
      </Heading>
      <FormControl id="event-name" isRequired>
        <FormLabel>Event Name</FormLabel>
        <Input
          type="text"
          value={eventName}
          onChange={(e) => setEventName(e.target.value)}
          placeholder="e.g., Alice & Bob's Wedding Speeches"
        />
      </FormControl>

      <FormControl id="event-type" isRequired>
        <FormLabel>Event Type</FormLabel>
        <Select
          value={eventType}
          onChange={(e) => setEventType(e.target.value)}
        >
          {eventTypes.map(type => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </Select>
      </FormControl>

      <FormControl id="event-date">
        <FormLabel>Event Date (Optional)</FormLabel>
        <Input
          type="date"
          value={eventDate}
          onChange={(e) => setEventDate(e.target.value)}
        />
      </FormControl>

      <Button
        type="submit"
        colorScheme="blue"
        isLoading={isLoading}
        loadingText="Creating..."
        w="100%"
      >
        Create Event
      </Button>
    </VStack>
  );
};

export default EventCreateForm;
