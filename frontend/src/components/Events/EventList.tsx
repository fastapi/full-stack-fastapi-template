import React from 'react'; // Removed useState, useEffect
import { useQuery } from '@tanstack/react-query';
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
  AlertDescription,
  AlertTitle,
} from '@chakra-ui/react';
import EventListItem from './EventListItem';
// No longer need to import CoordinationEventPublic from EventListItem, will use client's type
import { EventsService, CoordinationEventPublic, ApiError } from '../../client';
import { Link as RouterLink } from '@tanstack/react-router';

const EventList: React.FC = () => {
  const {
    data: events,
    isLoading,
    isError,
    error,
  } = useQuery<CoordinationEventPublic[], ApiError>({
    queryKey: ['events'],
    queryFn: async () => {
      // EventsService.listUserEvents returns CancelablePromise<EventsListUserEventsResponse>
      // EventsListUserEventsResponse is Array<CoordinationEventPublic>
      // The actual data is directly the response type.
      return EventsService.listUserEvents();
    },
  });

  if (isLoading) {
    return (
      <Box textAlign="center" p={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading your events...</Text>
      </Box>
    );
  }

  if (isError) {
    return (
      <Alert status="error" mt={4} variant="subtle" flexDirection="column" alignItems="center" justifyContent="center" textAlign="center" height="200px">
        <AlertIcon boxSize="40px" mr={0} />
        <AlertTitle mt={4} mb={1} fontSize="lg">
          Error Loading Events
        </AlertTitle>
        <AlertDescription maxWidth="sm">
          {error?.message || 'An unexpected error occurred. Please try again later.'}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <VStack spacing={6} align="stretch" p={5}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Heading as="h2" size="xl">
          Your Coordination Events
        </Heading>
        {/* Updated link to match Tanstack Router v0.0.1-beta.28+ structure */}
        <Button as={RouterLink} to="/_layout/events/create" colorScheme="blue">
          Create New Event
        </Button>
      </Box>

      {!events || events.length === 0 ? (
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
