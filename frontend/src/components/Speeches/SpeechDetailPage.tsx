import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link as RouterLink } from '@tanstack/react-router';
import {
  Box,
  Heading,
  Text,
  VStack,
  Spinner,
  Alert,
  AlertIcon,
  Textarea,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  useToast,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Divider,
  Tag,
} from '@chakra-ui/react';
// import { SpeechesService, SecretSpeechVersionCreate as ApiSecretSpeechVersionCreate } from '../../client'; // Step 7
// import { useAuth } from '../../hooks/useAuth';
import SpeechVersionHistory from './SpeechVersionHistory';
import {
    mockSpeeches,
    addMockSpeechVersion,
    currentUserId as appCurrentUserId, // Renamed to avoid conflict
    SecretSpeechPublicDetailed,
    SecretSpeechVersionData
} from '../../mocks/mockData';

// Placeholder interfaces (assuming backend provides current version details)
// SecretSpeechPublicDetailed is now imported from mockData
// If user is owner, current_version.speech_draft should be populated.
export interface SecretSpeechVersionData {
  id: string;
  version_number: number;
  speech_draft?: string; // Only for owner
  speech_tone: string;
  estimated_duration_minutes: number;
  created_at: string;
  creator_id: string;
}

export interface SecretSpeechPublicDetailed {
  id: string;
  event_id: string;
  creator_id: string;
  creator_name?: string; // Added for display
  created_at: string;
  updated_at: string;
  current_version_id?: string | null;
  current_version?: SecretSpeechVersionData | null; // Nested current version details
}

const speechTones = ["neutral", "sentimental", "humorous", "serious", "inspirational", "mixed", "other"];

// Mock data for a single speech detail
const mockSpeechDetailOwner: SecretSpeechPublicDetailed = {
// Removed direct mock data definitions here, will use imported mockSpeeches


const SpeechDetailPage: React.FC = () => {
  const { speechId } = useParams({ from: '/_layout/speeches/$speechId' }); // Adjusted 'from'
  // const { user } = useAuth();
  // const actualCurrentUserId = user?.id || appCurrentUserId; // Use from auth or mock
  const actualCurrentUserId = appCurrentUserId; // Using renamed mock currentUserId

  const [speech, setSpeech] = useState<SecretSpeechPublicDetailed | null>(null);
  const [editableDraft, setEditableDraft] = useState('');
  const [editableTone, setEditableTone] = useState('');
  const [editableDuration, setEditableDuration] = useState<number | string>(5);

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  const isCreator = speech?.creator_id === actualCurrentUserId;

  const fetchSpeechDetails = useCallback(async () => {
    if (!speechId) {
      setError('Speech ID not found in URL.');
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    console.log(`SpeechDetailPage: Fetching speech ${speechId}, current user ${actualCurrentUserId}`);
    try {
      await new Promise(resolve => setTimeout(resolve, 700)); // Simulate API
      const foundSpeech = mockSpeeches.find(s => s.id === speechId);

      if (foundSpeech) {
        // Simulate backend logic: only include draft if current user is creator
        const speechToSet = JSON.parse(JSON.stringify(foundSpeech)); // Deep copy for modification
        if (speechToSet.current_version && speechToSet.creator_id !== actualCurrentUserId) {
          delete speechToSet.current_version.speech_draft;
        }
        setSpeech(speechToSet);
        if (speechToSet.current_version) {
          setEditableDraft(speechToSet.current_version.speech_draft || (isCreator ? '' : 'Draft not available'));
          setEditableTone(speechToSet.current_version.speech_tone);
          setEditableDuration(speechToSet.current_version.estimated_duration_minutes);
        } else {
          setEditableDraft(isCreator ? '' : 'No current version to display.');
          setEditableTone(speechTones[0]);
          setEditableDuration(5);
        }
      } else {
        throw new Error('Speech not found in mock data.');
      }
    } catch (err) {
      console.error(`Failed to fetch speech details for ${speechId}:`, err);
      setError('Failed to load speech details.');
    } finally {
      setIsLoading(false);
    }
  }, [speechId, actualCurrentUserId, isCreator]); // Added isCreator to deps for safety on draft text

  useEffect(() => {
    fetchSpeechDetails();
  }, [fetchSpeechDetails]);

  const handleSaveChanges = async () => {
    if (!speech || !isCreator) return;
    setIsSaving(true);

    const currentVersionNumber = speech.current_version?.version_number || 0;
    const newVersionId = `v-mock-${speech.id}-${currentVersionNumber + 1}-${Date.now()}`;

    const newVersionData: SecretSpeechVersionData = {
        id: newVersionId,
        speech_id: speech.id,
        version_number: currentVersionNumber + 1,
        speech_draft: editableDraft,
        speech_tone: editableTone,
        estimated_duration_minutes: Number(editableDuration),
        created_at: new Date().toISOString(),
        creator_id: actualCurrentUserId, // Creator of the new version is the current user
    };

    try {
      console.log("Saving new version (mock):", newVersionData);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API

      addMockSpeechVersion(speech.id, newVersionData); // Update global mock store

      toast({ title: 'Changes Saved (Mock)', description: 'A new version of your speech has been created.', status: 'success' });
      fetchSpeechDetails(); // Refresh speech details to get the new current_version
    } catch (err) {
      console.error('Failed to save changes:', err);
      toast({ title: 'Save Failed (Mock)', description: 'Could not save your changes.', status: 'error'});
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) return <Spinner />;
  if (error) return <Alert status="error"><AlertIcon />{error}</Alert>;
  if (!speech) return <Alert status="info"><AlertIcon />No speech data found.</Alert>;

  return (
    <VStack spacing={5} align="stretch" p={5}>
      <Box p={4} borderWidth="1px" borderRadius="md" shadow="sm">
        <Heading as="h1" size="lg" mb={3}>
          Speech: {speech.creator_name ? `${speech.creator_name}'s Speech` : `Speech ID ${speech.id}`}
        </Heading>
        <Text><strong>Event Link:</strong> <RouterLink to={`/events/${speech.event_id}`}><Text as="span" color="blue.500" _hover={{textDecoration: "underline"}}>View Event</Text></RouterLink></Text>
        <Text><strong>Created by:</strong> {speech.creator_name || speech.creator_id} {isCreator && <Tag size="sm" colorScheme="green" ml={2}>Me</Tag>}</Text>
        <Text><strong>Created at:</strong> {new Date(speech.created_at).toLocaleString()}</Text>
        <Text><strong>Last updated:</strong> {new Date(speech.updated_at).toLocaleString()}</Text>
      </Box>

      <Tabs variant="line" colorScheme="teal">
        <TabList>
          <Tab>Current Version {isCreator ? "(Edit)" : "(View)"}</Tab>
          <Tab>Version History</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            {!speech.current_version && <Text>No current version available for this speech.</Text>}
            {speech.current_version && (
              <VStack spacing={4} align="stretch">
                <FormControl id="speech-tone" isReadOnly={!isCreator}>
                  <FormLabel>Speech Tone</FormLabel>
                  {isCreator ? (
                    <Select value={editableTone} onChange={(e) => setEditableTone(e.target.value)}>
                      {speechTones.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                    </Select>
                  ) : (
                    <Text>{speech.current_version.speech_tone}</Text>
                  )}
                </FormControl>

                <FormControl id="speech-duration" isReadOnly={!isCreator}>
                  <FormLabel>Estimated Duration (minutes)</FormLabel>
                  {isCreator ? (
                    <NumberInput
                        min={1}
                        value={editableDuration}
                        onChange={(valStr) => setEditableDuration(valStr ? parseInt(valStr) : '')}
                    >
                      <NumberInputField />
                      <NumberInputStepper><NumberIncrementStepper /><NumberDecrementStepper /></NumberInputStepper>
                    </NumberInput>
                  ) : (
                    <Text>{speech.current_version.estimated_duration_minutes} minutes</Text>
                  )}
                </FormControl>

                <FormControl id="speech-draft" isReadOnly={!isCreator}>
                  <FormLabel>Speech Draft</FormLabel>
                  {isCreator ? (
                    <Textarea
                      value={editableDraft}
                      onChange={(e) => setEditableDraft(e.target.value)}
                      rows={15}
                      placeholder="Write your speech draft here..."
                    />
                  ) : (
                    <Text fontStyle="italic" color="gray.600">
                      {speech.current_version.speech_draft ? speech.current_version.speech_draft : "Draft not available for viewing."}
                    </Text>
                  )}
                </FormControl>

                {isCreator && (
                  <Button colorScheme="teal" onClick={handleSaveChanges} isLoading={isSaving} loadingText="Saving...">
                    Save Changes (Creates New Version)
                  </Button>
                )}
              </VStack>
            )}
          </TabPanel>
          <TabPanel>
            <SpeechVersionHistory
              speechId={speech.id}
              currentUserId={actualCurrentUserId}
              isCreator={isCreator}
              currentSpeechVersionId={speech.current_version_id}
              onVersionSetAsCurrent={fetchSpeechDetails}
            />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </VStack>
  );
};

export default SpeechDetailPage;
