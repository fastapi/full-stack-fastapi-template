import React from 'react';
import { Box, Text, Heading, LinkBox, LinkOverlay, Tag, HStack, Avatar } from '@chakra-ui/react';
import { Link as RouterLink } from '@tanstack/react-router';
// import { UserContext } from '../../hooks/useAuth'; // To get current user ID for "isCreator" check

// Placeholder interface for SecretSpeechPublic
// This should ideally include creator's info and current version's metadata.
// The actual draft is not included here for general listing.
export interface SecretSpeechPublic {
  id: string; // Speech ID
  event_id: string;
  creator_id: string;
  current_version_id?: string | null;
  created_at: string; // ISO string
  updated_at: string; // ISO string
  // Denormalized or fetched separately for display:
  creator_name?: string; // e.g., "John Doe" or "User <uuid>"
  creator_avatar_url?: string; // Optional
  current_version_tone?: string;
  current_version_duration?: number;
}

interface SpeechListItemProps {
  speech: SecretSpeechPublic;
  currentUserId?: string; // Pass current user's ID to determine if they are the creator
}

const SpeechListItem: React.FC<SpeechListItemProps> = ({ speech, currentUserId }) => {
  const isCreator = speech.creator_id === currentUserId;

  // Fallback if creator name is not readily available
  const displayName = speech.creator_name || `User ${speech.creator_id.substring(0, 8)}...`;

  return (
    <LinkBox as="article" p={4} borderWidth="1px" rounded="md" _hover={{ shadow: 'lg', bg: 'teal.50' }}>
      <VStack align="start" spacing={2}>
        <HStack spacing={3} w="100%">
          <Avatar size="sm" name={displayName} src={speech.creator_avatar_url} />
          <Heading size="sm" noOfLines={1}>
            <LinkOverlay as={RouterLink} to={`/speeches/${speech.id}`}>
              Speech by {displayName}
            </LinkOverlay>
          </Heading>
          {isCreator && <Tag size="sm" colorScheme="green">My Speech</Tag>}
        </HStack>

        {speech.current_version_tone && (
          <Tag colorScheme="blue" size="sm">Tone: {speech.current_version_tone}</Tag>
        )}

        {speech.current_version_duration !== undefined && (
          <Text fontSize="sm" color="gray.600">
            Duration: {speech.current_version_duration} min
          </Text>
        )}

        {!speech.current_version_id && (
            <Text fontSize="sm" fontStyle="italic" color="gray.500">No current version available.</Text>
        )}

        <Text fontSize="xs" color="gray.400" pt={1}>
          Last updated: {new Date(speech.updated_at).toLocaleDateString()}
        </Text>
      </VStack>
    </LinkBox>
  );
};

export default SpeechListItem;
