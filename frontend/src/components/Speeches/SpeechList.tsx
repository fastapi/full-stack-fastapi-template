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
import React from 'react'; // Removed useState, useCallback, useEffect
import { useQuery, useQueryClient } from '@tanstack/react-query';
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
  HStack,
  AlertDescription,
  AlertTitle,
} from '@chakra-ui/react';
import SpeechListItem from './SpeechListItem';
import SpeechCreateForm from './SpeechCreateForm';
import { SpeechesService, SecretSpeechPublic, ApiError } from '../../../client';
// import { useAuth } from '../../../hooks/useAuth'; // For currentUserId

interface SpeechListProps {
  eventId: string;
}

const SpeechList: React.FC<SpeechListProps> = ({ eventId }) => {
  const { isOpen, onOpen, onClose } = useDisclosure(); // For SpeechCreateForm modal
  const queryClient = useQueryClient(); // To invalidate queries from child form

  // const { user } = useAuth();
  // const currentUserId = user?.id; // This would be the actual current user ID
  const currentUserId = 'user-123-alice'; // Using mock currentUserId for SpeechListItem prop

  const {
    data: speeches,
    isLoading,
    isError,
    error
  } = useQuery<SecretSpeechPublic[], ApiError>({
    queryKey: ['eventSpeeches', eventId],
    queryFn: async () => {
      if (!eventId) throw new Error("Event ID is required to fetch speeches.");
      // SpeechesService.listEventSpeeches expects SpeechesListEventSpeechesData: { eventId: string }
      return SpeechesService.listEventSpeeches({ eventId });
    },
    enabled: !!eventId,
  });

  const handleSpeechCreated = () => {
    onClose(); // Close the modal
    // Query invalidation is handled by SpeechCreateForm's useMutation's onSuccess
    // but if we need to ensure it happens even if form doesn't use queryClient itself:
    // queryClient.invalidateQueries({ queryKey: ['eventSpeeches', eventId] });
  };

  if (isLoading) {
    return (
      <Box textAlign="center" p={5}>
        <Spinner size="lg" />
        <Text mt={2}>Loading speeches...</Text>
      </Box>
    );
  }

  if (isError) {
    return (
      <Alert status="error" mt={4} variant="subtle" flexDirection="column" alignItems="center" justifyContent="center" textAlign="center" height="150px">
        <AlertIcon boxSize="30px" mr={0} />
        <AlertTitle mt={3} mb={1} fontSize="md">
          Error Loading Speeches
        </AlertTitle>
        <AlertDescription maxWidth="sm" fontSize="sm">
          {error?.body?.detail || error?.message || 'An unexpected error occurred.'}
        </AlertDescription>
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

      {!speeches || speeches.length === 0 ? (
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

      <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
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
