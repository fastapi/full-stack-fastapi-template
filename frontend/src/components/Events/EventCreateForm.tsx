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
import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  useToast,
  Select,
} from '@chakra-ui/react';
import { EventsService, CoordinationEventCreate, ApiError } from '../../client'; // Import client and types
// import { useNavigate } from '@tanstack/react-router'; // For redirect after creation

// Predefined event types - can be expanded
const eventTypes = [
  { value: "wedding_speech_pair", label: "Wedding Speech Pair" },
  { value: "vows_exchange", label: "Vows Exchange" },
  { value: "team_presentation", label: "Team Presentation" },
  { value: "debate_session", label: "Debate Session" },
  { value: "other", label: "Other" },
];

const EventCreateForm: React.FC = () => {
  const queryClient = useQueryClient();
  // const navigate = useNavigate(); // For redirect
  const toast = useToast();

  const [eventName, setEventName] = useState('');
  const [eventType, setEventType] = useState(eventTypes[0].value);
  const [eventDate, setEventDate] = useState('');

  const mutation = useMutation<
    CoordinationEventPublic, // Expected response type (adjust if needed, based on client)
    ApiError,
    CoordinationEventCreate // Input type to mutationFn
  >({
    mutationFn: async (newEventData: CoordinationEventCreate) => {
      // EventsService.createEvent expects EventsCreateEventData which has a requestBody property
      return EventsService.createEvent({ requestBody: newEventData });
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
      toast({
        title: 'Event Created',
        description: `Event "${data.event_name}" has been successfully created.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      setEventName('');
      setEventType(eventTypes[0].value);
      setEventDate('');
      // navigate({ to: '/_layout/events' }); // Example redirect
    },
    onError: (error) => {
      toast({
        title: 'Creation Failed',
        description: error.message || 'There was an error creating the event. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!eventName.trim() || !eventType) {
      toast({
        title: 'Missing fields',
        description: 'Event Name and Type are required.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    const eventData: CoordinationEventCreate = {
      event_name: eventName,
      event_type: eventType,
      // Ensure date is in 'YYYY-MM-DD' format if that's what backend expects for date-only.
      // If it's datetime, then toISOString() is fine.
      // The client type `CoordinationEventCreate` has `event_date: string`.
      // Assuming backend handles ISO string for datetime or YYYY-MM-DD for date.
      event_date: eventDate ? new Date(eventDate).toISOString() : new Date().toISOString(), // Defaulting to now if not set; adjust as needed
    };
    // If event_date is truly optional and backend handles missing field:
    // const eventData: CoordinationEventCreate = {
    //   event_name: eventName,
    //   event_type: eventType,
    //   ...(eventDate && { event_date: new Date(eventDate).toISOString() }),
    // };


    mutation.mutate(eventData);
  };

  return (
    <VStack spacing={4} as="form" onSubmit={handleSubmit} w="100%" maxW="md" m="auto">
      <Heading as="h2" size="lg" textAlign="center">
        Create New Coordination Event
      </Heading>
      <FormControl id="event-name" isRequired isInvalid={mutation.error?.body?.detail?.some((err: any) => err.loc?.includes('event_name'))}>
        <FormLabel>Event Name</FormLabel>
        <Input
          type="text"
          value={eventName}
          onChange={(e) => setEventName(e.target.value)}
          placeholder="e.g., Alice & Bob's Wedding Speeches"
          isDisabled={mutation.isPending}
        />
      </FormControl>

      <FormControl id="event-type" isRequired isInvalid={mutation.error?.body?.detail?.some((err: any) => err.loc?.includes('event_type'))}>
        <FormLabel>Event Type</FormLabel>
        <Select
          value={eventType}
          onChange={(e) => setEventType(e.target.value)}
          isDisabled={mutation.isPending}
        >
          {eventTypes.map(type => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </Select>
      </FormControl>

      <FormControl id="event-date" isInvalid={mutation.error?.body?.detail?.some((err: any) => err.loc?.includes('event_date'))}>
        <FormLabel>Event Date</FormLabel>
        <Input
          type="date" // HTML5 date picker expects YYYY-MM-DD
          value={eventDate}
          onChange={(e) => setEventDate(e.target.value)}
          isDisabled={mutation.isPending}
        />
      </FormControl>

      <Button
        type="submit"
        colorScheme="blue"
        isLoading={mutation.isPending}
        loadingText="Creating..."
        w="100%"
      >
        Create Event
      </Button>
    </VStack>
  );
};

export default EventCreateForm;
