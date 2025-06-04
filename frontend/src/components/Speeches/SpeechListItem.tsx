import React from 'react';
import { Box, Text, Heading, LinkBox, LinkOverlay, Tag, HStack, Avatar } from '@chakra-ui/react';
import { Link as RouterLink } from '@tanstack/react-router';
import { SecretSpeechPublic } from '../../../client'; // Use type from generated client
// import { useAuth } from '../../../hooks/useAuth'; // For currentUserId

interface SpeechListItemProps {
  speech: SecretSpeechPublic; // This type from client does NOT have creator_name, tone, duration directly
  currentUserId?: string;
}

const SpeechListItem: React.FC<SpeechListItemProps> = ({ speech, currentUserId }) => {
  const isCreator = speech.creator_id === currentUserId;
  // const { data: user } = useQuery(['user', speech.creator_id], () => UsersService.readUserById({userId: speech.creator_id}), { enabled: !!speech.creator_id })
  // const creatorDisplayName = user?.full_name || user?.email || speech.creator_id;
  // For now, to avoid N+1 fetching in list, just show creator ID or generic name
  const creatorDisplayName = `User ${speech.creator_id.substring(0, 8)}...`;

  // To get current_version_tone and duration, another fetch would be needed per item, or backend needs to provide it.
  // For now, these fields will not be displayed in the list item directly from this prop.
  // They are available on SpeechDetailPage.

  return (
    <LinkBox as="article" p={4} borderWidth="1px" rounded="md" _hover={{ shadow: 'lg', bg: 'teal.50' }}>
      <VStack align="start" spacing={2}>
        <HStack spacing={3} w="100%">
          <Avatar size="sm" name={creatorDisplayName} /> {/* Basic avatar based on ID */}
          <Heading size="sm" noOfLines={1}>
            {/* Updated link to match Tanstack Router structure */}
            <LinkOverlay as={RouterLink} to={`/_layout/speeches/${speech.id}`}>
              Speech by {creatorDisplayName}
            </LinkOverlay>
          </Heading>
          {isCreator && <Tag size="sm" colorScheme="green">My Speech</Tag>}
        </HStack>

        <Text fontSize="xs" color="gray.500">
            Event ID: {speech.event_id.substring(0,8)}...
        </Text>

        {!speech.current_version_id && (
            <Tag size="sm" colorScheme="orange">No active version</Tag>
        )}
         {speech.current_version_id && (
            <Tag size="sm" colorScheme="gray">Version ID: {speech.current_version_id.substring(0,8)}...</Tag>
        )}

        <Text fontSize="xs" color="gray.400" pt={1}>
          Last updated: {new Date(speech.updated_at).toLocaleDateString()}
        </Text>
      </VStack>
    </LinkBox>
  );
};

export default SpeechListItem;
