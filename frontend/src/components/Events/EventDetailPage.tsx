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
// import { EventsService } from '../../client'; // Step 7
import { CoordinationEventPublic } from './EventListItem'; // Reuse existing interface
import EventParticipantManager from './EventParticipantManager';
import SpeechList from '../Speeches/SpeechList'; // Added for integration
import SpeechAnalysisDisplay from '../Analysis/SpeechAnalysisDisplay'; // Added for integration
import { modifiableMockEvents, currentUserId } from '../../mocks/mockData'; // Import mock data

const EventDetailPage: React.FC = () => {
  const { eventId } = useParams({ from: '/_layout/events/$eventId' }); // Adjusted 'from' to match route definition

  const [event, setEvent] = useState<CoordinationEventPublic | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // const { user } = useAuth(); // For currentUserId
  // const actualCurrentUserId = user?.id || currentUserId;
  const actualCurrentUserId = currentUserId; // Using mock

  useEffect(() => {
    if (!eventId) {
      setError('Event ID not found in URL.');
      setIsLoading(false);
      return;
    }

    const fetchEventDetails = async () => {
      setIsLoading(true);
      setError(null);
      try {
        console.log(`EventDetailPage: Fetching event ${eventId}`);
        await new Promise(resolve => setTimeout(resolve, 750));
        const foundEvent = modifiableMockEvents.find(e => e.id === eventId);
        if (foundEvent) {
          setEvent(foundEvent);
        } else {
          throw new Error("Event not found in mock data");
        }
      } catch (err) {
        console.error(`Failed to fetch event details for ${eventId}:`, err);
        setError(`Failed to load event details. Please check the event ID or try again later.`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEventDetails();
  }, [eventId]);

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString(undefined, {
        year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <Box textAlign="center" p={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading event details...</Text>
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

  if (!event) {
    return (
      <Alert status="warning" mt={4}>
        <AlertIcon />
        No event data available.
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
