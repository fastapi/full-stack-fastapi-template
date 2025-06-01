import React, { useEffect, useState, useCallback } from 'react';
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
} from '@chakra-ui/react';
// import { SpeechesService, SecretSpeechVersionPublic as ApiVersion } from '../../client'; // Step 7
import {
    mockSpeechVersionsStore,
    setMockSpeechCurrentVersion,
    SecretSpeechVersionHistoryItem // Using the interface from mockData
} from '../../mocks/mockData';


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
    currentSpeechVersionId, // This prop correctly identifies the active version
    onVersionSetAsCurrent
}) => {
  const [versions, setVersions] = useState<SecretSpeechVersionHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure(); // For View Draft modal
  const [selectedDraft, setSelectedDraft] = useState<string | undefined>('');

  const fetchVersions = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    console.log(`SpeechVersionHistory: Fetching versions for speech ${speechId}. Current version is ${currentSpeechVersionId}`);
    try {
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API
      const speechSpecificVersions = mockSpeechVersionsStore[speechId] || [];

      // Sort by version_number descending to show newest first
      const sortedVersions = [...speechSpecificVersions].sort((a, b) => b.version_number - a.version_number);

      // Simulate draft privacy: only creator sees drafts of past versions
      const processedVersions = sortedVersions.map(v => {
        if (!isCreator && v.id !== currentSpeechVersionId) { // Non-creator doesn't see drafts of non-current versions
          return { ...v, speech_draft: undefined };
        }
        // If it IS the current version, SpeechDetailPage handles its draft privacy.
        // Here, we assume if isCreator is false, the draft for current might also be hidden by parent or backend.
        // For simplicity, if isCreator is true, they can see all their drafts from history.
        return v;
      });
      setVersions(processedVersions);
    } catch (err) {
      console.error(`Failed to fetch versions for speech ${speechId}:`, err);
      setError('Failed to load version history.');
    } finally {
      setIsLoading(false);
    }
  }, [speechId, isCreator]);

  useEffect(() => {
    fetchVersions();
  }, [fetchVersions]);

  const handleSetAsCurrent = async (versionId: string) => {
    if (!isCreator) return;
    try {
      console.log(`Setting version ${versionId} as current for speech ${speechId} (mock)`);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API
      setMockSpeechCurrentVersion(speechId, versionId); // Update global mock store

      toast({ title: 'Version Updated (Mock)', description: `Version has been set as current.`, status: 'success' });
      if (onVersionSetAsCurrent) {
        onVersionSetAsCurrent(); // Trigger refresh in parent (SpeechDetailPage)
      }
      // fetchVersions(); // Re-fetch local list - parent will trigger our re-fetch via prop change if needed
    } catch (err) {
      console.error('Failed to set version as current:', err);
      toast({ title: 'Update Failed (Mock)', description: 'Could not set version as current.', status: 'error' });
    }
  };

  const handleViewDraft = (draft?: string) => {
    if (!isCreator && !draft) { // Double check, though button shouldn't show
        setSelectedDraft("Draft not available for viewing.");
    } else {
        setSelectedDraft(draft || "No draft content for this version.");
    }
    onOpen();
  };

  if (isLoading) return <Spinner />;
  if (error) return <Alert status="error"><AlertIcon />{error}</Alert>;

  return (
    <Box>
      <Heading size="md" mb={4}>Version History</Heading>
      {versions.length === 0 ? (
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
                    {(isCreator || version.id === currentSpeechVersionId) && version.speech_draft && ( // Allow viewing current version draft for non-creator if available
                      <Button size="xs" variant="outline" onClick={() => handleViewDraft(version.speech_draft)}>
                        View Draft
                      </Button>
                    )}
                    {isCreator && version.id !== currentSpeechVersionId && (
                      <Button size="xs" colorScheme="blue" variant="outline" onClick={() => handleSetAsCurrent(version.id)}>
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

      {/* Modal for Viewing Draft - available to creator, or for current version if draft is passed */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>View Speech Draft</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Textarea value={selectedDraft} isReadOnly rows={20} whiteSpace="pre-wrap" />
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
