import React, { useEffect, useState } from 'react';
import { useParams } from '@tanstack/react-router'; // For accessing route parameters
import {
  Box,
  Heading,
  Text,
  VStack,
  Spinner,
  Alert,
  AlertIcon,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Divider,
} from '@chakra-ui/react';
import React from 'react'; // Removed useState, useEffect
import { useParams } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Heading,
  Text,
  VStack,
  Spinner,
  Alert,
  AlertIcon,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Divider,
  AlertDescription,
  AlertTitle,
} from '@chakra-ui/react';
import { EventsService, CoordinationEventPublic, ApiError } from '../../client';
import EventParticipantManager from './EventParticipantManager';
import SpeechList from '../Speeches/SpeechList';
import SpeechAnalysisDisplay from '../Analysis/SpeechAnalysisDisplay';
// No longer need mockEvents for this component's direct data fetching
// import { currentUserId } from '../../mocks/mockData';

const EventDetailPage: React.FC = () => {
  const { eventId } = useParams({ from: '/_layout/events/$eventId' });
  // const { user } = useAuth(); // For currentUserId if needed for permissions on this page directly
  // const actualCurrentUserId = user?.id || currentUserId; // Using mock

  const {
    data: event,
    isLoading,
    isError,
    error
  } = useQuery<CoordinationEventPublic, ApiError>({
    queryKey: ['event', eventId],
    queryFn: async () => {
      if (!eventId) {
        throw new Error("Event ID is not available.");
      }
      // EventsService.getEventDetails expects EventsGetEventDetailsData: { eventId: string }
      return EventsService.getEventDetails({ eventId });
    },
    enabled: !!eventId, // Only run query if eventId is available
    // Optional: staleTime, cacheTime, etc.
  });

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    // Using toLocaleString for date and time, toLocaleDateString for date only
    return new Date(dateString).toLocaleString(undefined, {
        year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: '2-digit'
    });
  };

  const formatJustDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
     return new Date(dateString).toLocaleDateString(undefined, {
        year: 'numeric', month: 'long', day: 'numeric'
    });
  }

  if (!eventId) { // Handle case where eventId might not be ready from router
    return (
      <Alert status="warning" mt={4}>
        <AlertIcon />
        <AlertTitle>Missing Event ID</AlertTitle>
        <AlertDescription>The event ID is missing from the URL.</AlertDescription>
      </Alert>
    );
  }

  if (isLoading) {
    return (
      <Box textAlign="center" p={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading event details for ID: {eventId}...</Text>
      </Box>
    );
  }

  if (isError) {
    return (
       <Alert status="error" mt={4} variant="subtle" flexDirection="column" alignItems="center" justifyContent="center" textAlign="center" height="200px">
        <AlertIcon boxSize="40px" mr={0} />
        <AlertTitle mt={4} mb={1} fontSize="lg">
          Error Loading Event
        </AlertTitle>
        <AlertDescription maxWidth="sm">
          {error?.body?.detail || error?.message || 'An unexpected error occurred.'}
          {error?.status === 404 && " The event was not found."}
        </AlertDescription>
      </Alert>
    );
  }

  if (!event) { // Should be covered by isLoading or isError, but as a fallback
    return (
      <Alert status="info" mt={4}>
        <AlertIcon />
        No event data available, or event not found.
      </Alert>
    );
  }

  return (
    <VStack spacing={6} align="stretch" p={5}>
      <Heading as="h1" size="xl" mb={4}>
        {event.event_name}
      </Heading>
      <Box p={4} borderWidth="1px" borderRadius="md" shadow="sm">
        <Text fontSize="lg"><strong>Type:</strong> {event.event_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</Text>
        <Text fontSize="md" color="gray.600"><strong>Date:</strong> {formatDate(event.event_date)}</Text>
        <Text fontSize="sm" color="gray.500"><strong>Created:</strong> {formatDate(event.created_at)}</Text>
        <Text fontSize="sm" color="gray.500"><strong>Last Updated:</strong> {formatDate(event.updated_at)}</Text>
        <Text fontSize="xs" color="gray.400" mt={2}>Event ID: {event.id}</Text>
        <Text fontSize="xs" color="gray.400">Creator ID: {event.creator_id}</Text>
      </Box>

      <Divider my={6} />

      <Tabs variant="enclosed-colored" colorScheme="blue">
        <TabList>
          <Tab>Participants</Tab>
          <Tab>Speeches</Tab>
          <Tab>Analysis & Nudges</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            <EventParticipantManager eventId={event.id} /> {/* currentUserId can be passed if needed by manager */}
          </TabPanel>
          <TabPanel>
            <SpeechList eventId={event.id} />
          </TabPanel>
          <TabPanel>
            <SpeechAnalysisDisplay eventId={event.id} />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </VStack>
  );
};

export default EventDetailPage;
