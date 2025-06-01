import React from 'react';
import { Box, Text, Heading, LinkBox, LinkOverlay } from '@chakra-ui/react';
import { Link as RouterLink } from '@tanstack/react-router'; // Assuming usage for navigation

import { CoordinationEventPublic } from '../../client'; // Import type from generated client

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
        {/* Updated link to match Tanstack Router v0.0.1-beta.28+ structure */}
        <LinkOverlay as={RouterLink} to={`/_layout/events/${event.id}`}>
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
