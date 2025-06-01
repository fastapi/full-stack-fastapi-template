import React, { useState } from 'react'; // Removed useEffect, useCallback
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Text,
  VStack,
  Spinner,
  Alert,
  AlertIcon,
  Button,
  useToast,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Tag,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Textarea,
  Heading,
  AlertDescription,
  AlertTitle,
} from '@chakra-ui/react';
import { SpeechesService, SecretSpeechVersionPublic, SecretSpeechPublic as SecretSpeechDetailPublic, ApiError } from '../../../client';

interface SpeechVersionHistoryProps {
  speechId: string;
  currentUserId: string;
  isCreator: boolean;
  currentSpeechVersionId?: string | null;
  onVersionSetAsCurrent?: () => void;
}

const SpeechVersionHistory: React.FC<SpeechVersionHistoryProps> = ({
    speechId,
    isCreator,
    currentSpeechVersionId,
    onVersionSetAsCurrent
}) => {
  const queryClient = useQueryClient();
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedDraft, setSelectedDraft] = useState<string | undefined>('');

  const {
    data: versions,
    isLoading,
    isError,
    error
  } = useQuery<SecretSpeechVersionPublic[], ApiError>({
    queryKey: ['speechVersions', speechId],
    queryFn: async () => {
      if (!speechId) throw new Error("Speech ID is required to fetch versions.");
      return SpeechesService.listSpeechVersions({ speechId });
    },
    enabled: !!speechId,
    select: (data) => [...data].sort((a, b) => b.version_number - a.version_number), // Show newest first
  });

  const setCurrentVersionMutation = useMutation<
    SecretSpeechDetailPublic,
    ApiError,
    { versionId: string }
  >({
    mutationFn: async ({ versionId }) => {
      if (!speechId) throw new Error("Speech ID is missing.");
      return SpeechesService.setCurrentSpeechVersion({ speechId, versionId });
    },
    onSuccess: () => {
      toast({ title: 'Version Updated', description: 'This version is now set as current.', status: 'success' });
      queryClient.invalidateQueries({ queryKey: ['speech', speechId] });
      queryClient.invalidateQueries({ queryKey: ['speechVersions', speechId] });
      if (onVersionSetAsCurrent) {
        onVersionSetAsCurrent();
      }
    },
    onError: (error) => {
      toast({ title: 'Update Failed', description: error.body?.detail?.[0]?.msg || error.message, status: 'error' });
    },
  });

  const handleSetAsCurrentClick = (versionId: string) => {
    if (!isCreator) return;
    setCurrentVersionMutation.mutate({ versionId });
  };

  const handleViewDraftClick = (version: SecretSpeechVersionPublic) => {
    // Backend controls draft visibility in the fetched `version.speech_draft`
    // If `isCreator` is true, backend should send the draft.
    // If `isCreator` is false, backend should not send draft for non-current versions.
    // For current version draft for non-creator, `SpeechDetailPage` logic applies.
    setSelectedDraft(version.speech_draft || "Draft not available for this version.");
    onOpen();
  };

  if (isLoading) return (
    <Box textAlign="center" p={5}><Spinner size="lg" /><Text mt={2}>Loading version history...</Text></Box>
  );

  if (isError) return (
    <Alert status="error" mt={4}>
      <AlertIcon />
      <AlertTitle>Error Loading Versions</AlertTitle>
      <AlertDescription>{error?.body?.detail?.[0]?.msg || error?.message}</AlertDescription>
    </Alert>
  );

  return (
    <Box>
      <Heading size="md" mb={4}>Version History</Heading>
      {!versions || versions.length === 0 ? (
        <Text>No version history found for this speech.</Text>
      ) : (
        <Table variant="simple" size="sm">
          <Thead>
            <Tr>
              <Th>Version</Th>
              <Th>Tone</Th>
              <Th>Duration (min)</Th>
              <Th>Created At</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {versions.map((version) => (
              <Tr key={version.id} bg={version.id === currentSpeechVersionId ? 'teal.100' : 'transparent'} _hover={{bg: "gray.50"}}>
                <Td>
                  {version.version_number}
                  {version.id === currentSpeechVersionId && <Tag size="sm" colorScheme="teal" ml={2}>Current</Tag>}
                </Td>
                <Td>{version.speech_tone}</Td>
                <Td>{version.estimated_duration_minutes}</Td>
                <Td>{new Date(version.created_at).toLocaleString()}</Td>
                <Td>
                  <VStack align="start" spacing={1}>
                    {version.speech_draft && ( // Only show button if draft is available (backend controls this for creator)
                      <Button size="xs" variant="outline" onClick={() => handleViewDraftClick(version)}>
                        View Draft
                      </Button>
                    )}
                    {isCreator && version.id !== currentSpeechVersionId && (
                      <Button
                        size="xs"
                        colorScheme="blue"
                        variant="outline"
                        onClick={() => handleSetAsCurrentClick(version.id)}
                        isLoading={setCurrentVersionMutation.isPending && setCurrentVersionMutation.variables?.versionId === version.id}
                      >
                        Set as Current
                      </Button>
                    )}
                  </VStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      )}

      <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>View Speech Draft</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Textarea value={selectedDraft} isReadOnly rows={20} whiteSpace="pre-wrap" fontFamily="monospace" />
          </ModalBody>
          <ModalFooter>
            <Button onClick={onClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default SpeechVersionHistory;
