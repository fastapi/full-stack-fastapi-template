import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Heading,
  VStack,
  Text,
  Spinner,
  Alert,
  AlertIcon,
  SimpleGrid,
} from '@chakra-ui/react';
import EventListItem, { CoordinationEventPublic } from './EventListItem'; // Import the item component and its type
// import { EventsService } from '../../client'; // Step 7
import { Link as RouterLink } from '@tanstack/react-router'; // For "Create New" button
import { modifiableMockEvents, currentUserId, mockParticipants } from '../../mocks/mockData'; // Using shared mock data & mockParticipants

const EventList: React.FC = () => {
  // const { user } = useAuth(); // To get currentUserId for filtering if API returns all events
  // For mock, we assume API would return events for the current user, or we filter them here.
  // The backend `get_user_events` already filters by participation.
  const [events, setEvents] = useState<CoordinationEventPublic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Simulate API call
        console.log("EventList: Fetching events for user:", currentUserId);
        await new Promise(resolve => setTimeout(resolve, 750));

        // Filter events to show only those where the current user is a participant or creator
        const userEventIds = new Set<string>();
        mockParticipants.forEach(p => {
            if (p.user_id === currentUserId) {
                userEventIds.add(p.event_id);
            }
        });

        modifiableMockEvents.forEach(event => {
            if (event.creator_id === currentUserId) {
                userEventIds.add(event.id);
            }
        });

        const userVisibleEvents = modifiableMockEvents.filter(event => userEventIds.has(event.id));
        setEvents(userVisibleEvents);
      } catch (err) {
        console.error('Failed to fetch events:', err);
        setError('Failed to load events. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvents();
    // Dependency array should be empty if we only fetch once on mount.
    // If `modifiableMockEvents` could change from outside due to other components
    // and we want this list to reflect that without a full page reload or prop drilling,
    // a more complex state management (like Zustand, Redux, or React Context) would be needed.
    // For now, this basic fetch-once is fine for mock data.
  }, []);

  if (isLoading) {
    return (
      <Box textAlign="center" p={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading your events...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error" mt={4}>
        <AlertIcon />
        {error}
      </Alert>
    );
  }

  return (
    <VStack spacing={6} align="stretch" p={5}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Heading as="h2" size="xl">
          Your Coordination Events
        </Heading>
        <Button as={RouterLink} to="/events/create" colorScheme="blue"> {/* Assuming a route for creation */}
          Create New Event
        </Button>
      </Box>

      {events.length === 0 ? (
        <Text fontSize="lg" color="gray.500" textAlign="center" p={10}>
          You are not part of any coordination events yet. Why not create one?
        </Text>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
          {events.map((event) => (
            <EventListItem key={event.id} event={event} />
          ))}
        </SimpleGrid>
      )}
    </VStack>
  );
};

export default EventList;
