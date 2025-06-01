import React, { useEffect, useState, useCallback } from 'react';
import {
  VStack,
  Text,
  Spinner,
  Alert,
  AlertIcon,
  SimpleGrid,
  Heading,
  Box,
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  useDisclosure,
} from '@chakra-ui/react';
import SpeechListItem from './SpeechListItem'; // SecretSpeechPublic is imported from mockData now
import SpeechCreateForm from './SpeechCreateForm'; // To add a new speech
// import { SpeechesService, SecretSpeechPublicDetailed } from '../../client'; // Step 7
// import { useAuth } from '../../hooks/useAuth';
import { mockSpeeches as globalMockSpeeches, currentUserId, SecretSpeechPublicDetailed } from '../../mocks/mockData'; // Use detailed for consistency if needed by item

interface SpeechListProps {
  eventId: string;
}


const SpeechList: React.FC<SpeechListProps> = ({ eventId }) => {
  const [speeches, setSpeeches] = useState<SecretSpeechPublicDetailed[]>([]); // Use detailed type
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure(); // For SpeechCreateForm modal

  // const { user } = useAuth();
  // const actualCurrentUserId = user?.id || currentUserId;
  const actualCurrentUserId = currentUserId; // Using mock currentUserId for owner checks

  const fetchSpeeches = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      console.log(`SpeechList: Fetching speeches for event ${eventId}`);
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call

      setSpeeches(globalMockSpeeches.filter(s => s.event_id === eventId));
    } catch (err) {
      console.error(`Failed to fetch speeches for event ${eventId}:`, err);
      setError('Failed to load speeches. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  }, [eventId]);

  useEffect(() => {
    fetchSpeeches();
  }, [fetchSpeeches]);

  const handleSpeechCreated = () => {
    onClose(); // Close the modal
    fetchSpeeches(); // Refresh the list of speeches
  };

  if (isLoading) {
    return (
      <Box textAlign="center" p={5}>
        <Spinner size="lg" />
        <Text mt={2}>Loading speeches...</Text>
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
    <VStack spacing={4} align="stretch">
      <HStack justifyContent="space-between" alignItems="center" mb={2}>
        <Heading as="h3" size="lg">
          Speeches for this Event
        </Heading>
        <Button colorScheme="teal" onClick={onOpen}>
          Add My Speech
        </Button>
      </HStack>

      {speeches.length === 0 ? (
        <Text fontSize="md" color="gray.500" p={5} borderWidth="1px" borderRadius="md" textAlign="center">
          No speeches have been added to this event yet.
        </Text>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
          {speeches.map((speech) => (
            <SpeechListItem key={speech.id} speech={speech} currentUserId={currentUserId} />
          ))}
        </SimpleGrid>
      )}

      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add Your Speech</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <SpeechCreateForm eventId={eventId} onSpeechCreated={handleSpeechCreated} />
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default SpeechList;
