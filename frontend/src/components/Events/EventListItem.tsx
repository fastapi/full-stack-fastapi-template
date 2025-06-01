import React from 'react';
import { Box, Text, Heading, LinkBox, LinkOverlay } from '@chakra-ui/react';
import { Link as RouterLink } from '@tanstack/react-router'; // Assuming usage for navigation

// Interface based on CoordinationEventPublic schema (backend/app/models.py)
// Replace with actual import from client when available (Step 7)
export interface CoordinationEventPublic {
  id: string; // Assuming UUID is string
  event_name: string;
  event_type: string;
  event_date?: string; // ISO string
  creator_id: string;
  created_at: string; // ISO string
  updated_at: string; // ISO string
}

interface EventListItemProps {
  event: CoordinationEventPublic;
}

const EventListItem: React.FC<EventListItemProps> = ({ event }) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Date not set';
    try {
      return new Date(dateString).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch (error) {
      console.error("Error formatting date:", dateString, error);
      return "Invalid date";
    }
  };

  return (
    <LinkBox as="article" p={5} borderWidth="1px" rounded="md" _hover={{ shadow: 'md', bg: 'gray.50' }}>
      <Heading size="md" my={2}>
        <LinkOverlay as={RouterLink} to={`/events/${event.id}`}>
          {event.event_name}
        </LinkOverlay>
      </Heading>
      <Text mb={2}>
        <strong>Type:</strong> {event.event_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
      </Text>
      <Text fontSize="sm" color="gray.600">
        <strong>Date:</strong> {formatDate(event.event_date)}
      </Text>
      <Text fontSize="xs" color="gray.500" mt={2}>
        Event ID: {event.id}
      </Text>
    </LinkBox>
  );
};

export default EventListItem;
