import React, { useEffect, useState } from 'react'; // Keep useState for form fields
import { useParams, Link as RouterLink } from '@tanstack/react-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
  AlertDescription,
  AlertTitle,
} from '@chakra-ui/react';
import {
    SpeechesService,
    SecretSpeechPublic,
    SecretSpeechVersionCreate,
    SecretSpeechVersionPublic, // For fetching current version details
    ApiError
} from '../../../client';
// import { useAuth } from '../../../hooks/useAuth';
import SpeechVersionHistory from './SpeechVersionHistory';
import { currentUserId as mockAppCurrentUserId } from '../../../mocks/mockData'; // For testing ownership

const speechTones = ["neutral", "sentimental", "humorous", "serious", "inspirational", "mixed", "other"];

const SpeechDetailPage: React.FC = () => {
  const { speechId } = useParams({ from: '/_layout/speeches/$speechId' });
  const queryClient = useQueryClient();
  const toast = useToast();
  // const { user } = useAuth();
  // const currentUserId = user?.id;
  const currentUserId = mockAppCurrentUserId; // Using mock for ownership check

  const [editableDraft, setEditableDraft] = useState('');
  const [editableTone, setEditableTone] = useState(speechTones[0]);
  const [editableDuration, setEditableDuration] = useState<number | string>(5);

  // Query for the main speech data
  const {
    data: speech,
    isLoading: isLoadingSpeech,
    isError: isSpeechError,
    error: speechError,
    refetch: refetchSpeechBase, // To refetch after version set as current from history
  } = useQuery<SecretSpeechPublic, ApiError>({
    queryKey: ['speech', speechId],
    queryFn: async () => {
      if (!speechId) throw new Error("Speech ID is required.");
      return SpeechesService.getSpeechDetails({ speechId });
    },
    enabled: !!speechId,
  });

  const isCreator = speech?.creator_id === currentUserId;

  // Query for the current version's details, enabled only if speech and current_version_id exist
  const {
    data: currentVersionDetails,
    isLoading: isLoadingCurrentVersion
  } = useQuery<SecretSpeechVersionPublic, ApiError>({
    queryKey: ['speechVersion', speech?.current_version_id],
    queryFn: async () => {
      if (!speech?.current_version_id) throw new Error("Current version ID is missing.");
      // Assuming an endpoint like getSpeechVersion exists or listSpeechVersions can be used
      // For now, let's assume listSpeechVersions and find it, or a direct getSpeechVersion endpoint
      // This is a gap if SpeechesService.getSpeechVersion({ versionId: speech.current_version_id }) doesn't exist.
      // The client has listSpeechVersions({speechId}), not getSpeechVersion({versionId}).
      // We will use listSpeechVersions and filter, or assume SpeechVersionHistory provides it.
      // To simplify, we will rely on SpeechVersionHistory to load all versions, and find current one there.
      // OR, if backend sends current_version_draft for owner with getSpeechDetails, it's easier.
      // Let's assume for now, the draft for editing is fetched by SpeechVersionHistory or manually entered.
      // The `onSuccess` of main speech query will attempt to set form fields.
      // This query is more for if we need to explicitly re-fetch current version data separately with its own loading.
      // For now, we'll assume the main 'speech' query's onSuccess and SpeechVersionHistory handle populating editables.
      // This part will be tricky without a direct getSpeechVersion(versionId) or richer getSpeechDetails response.
      // Let's assume backend returns draft in getSpeechDetails if user is owner.
      // And if not, SpeechVersionHistory is primary source for viewing specific old versions.
      // The `useEffect` below will handle setting editable fields from `speech` or `currentVersionDetails`.
      // This query might be redundant if `speech` object from `getSpeechDetails` is rich enough for owners.
      // If `SpeechesService.getSpeechDetails` already returns current_version_draft for owner, this is not needed.
      // The task description implies `getSpeechDetails` should return draft for owner.
      // So, we'll populate from `speech` object's assumed `current_version` (if backend adds it)
      // or from `currentVersionDetails` if we had a separate fetch for it.
      // Sticking to task: "speech ... should ideally include details of the current_version ... draft if current user is owner"
      // So, `speech.current_version.speech_draft` is assumed to be populated by backend for owner.
      // This query for currentVersionDetails can be removed if that assumption holds.
      // For now, removing this separate query for currentVersionDetails.
      throw new Error("This separate query for current version details might not be needed if getSpeechDetails is rich enough.");
    },
    enabled: false, // Disabled for now, relying on main speech query and future SpeechVersionHistory logic
  });

  // Effect to update form fields when speech data is loaded or changes
  useEffect(() => {
    if (speech) {
      const cv = (speech as any).current_version; // Cast to any if current_version is not on client's SecretSpeechPublic
      if (isCreator) {
        setEditableDraft(cv?.speech_draft || '');
        setEditableTone(cv?.speech_tone || speechTones[0]);
        setEditableDuration(cv?.estimated_duration_minutes || 5);
      } else {
        // For non-creators, draft is not shown. Tone/duration might be from current_version if available.
        setEditableDraft("Draft not available for viewing.");
        setEditableTone(cv?.speech_tone || speechTones[0]);
        setEditableDuration(cv?.estimated_duration_minutes || 5);
      }
    }
  }, [speech, isCreator]);

  const createVersionMutation = useMutation<
    SecretSpeechVersionPublic,
    ApiError,
    SecretSpeechVersionCreate
  >({
    mutationFn: async (newVersionData: SecretSpeechVersionCreate) => {
      if (!speechId) throw new Error("Speech ID is missing.");
      return SpeechesService.createSpeechVersion({ speechId, requestBody: newVersionData });
    },
    onSuccess: () => {
      toast({ title: 'Changes Saved', description: 'A new version of your speech has been created.', status: 'success' });
      queryClient.invalidateQueries({ queryKey: ['speech', speechId] });
      queryClient.invalidateQueries({ queryKey: ['speechVersions', speechId] });
    },
    onError: (error) => {
      toast({ title: 'Save Failed', description: error.body?.detail?.[0]?.msg || error.message, status: 'error'});
    }
  });

  const handleSaveChanges = () => {
    if (!isCreator) return;
    const newVersionPayload: SecretSpeechVersionCreate = {
        speech_draft: editableDraft,
        speech_tone: editableTone,
        estimated_duration_minutes: Number(editableDuration),
    };
    createVersionMutation.mutate(newVersionPayload);
  };

  const handleVersionSetAsCurrent = () => {
    queryClient.invalidateQueries({ queryKey: ['speech', speechId] }); // Re-fetch main speech details
    refetchSpeechBase(); // Explicitly call refetch from the speech query
  };

  if (isLoadingSpeech) return (
    <Box textAlign="center" p={10}><Spinner size="xl" /><Text mt={2}>Loading speech...</Text></Box>
  );

  if (isSpeechError) return (
    <Alert status="error" mt={4} variant="subtle" flexDirection="column" alignItems="center" justifyContent="center" textAlign="center" height="200px">
      <AlertIcon boxSize="40px" mr={0} />
      <AlertTitle mt={4} mb={1} fontSize="lg">Error Loading Speech</AlertTitle>
      <AlertDescription maxWidth="sm">{speechError?.body?.detail?.[0]?.msg || speechError?.message}</AlertDescription>
    </Alert>
  );

  if (!speech) return (
    <Alert status="info" mt={4}><AlertIcon />Speech data not found or not yet loaded.</Alert>
  );

  // Assuming `speech.current_version` object with tone, duration, and draft (for owner)
  // would be populated by the backend if it's part of a custom `SecretSpeechPublicDetailed` response.
  // Since client `SecretSpeechPublic` does not have this, we rely on `editableDraft` etc. state,
  // which are set in `useEffect` based on the assumption that `speech` (if detailed enough) or
  // `currentVersionDetails` (if fetched separately) would provide these.
  const displayCurrentTone = isCreator ? editableTone : ((speech as any).current_version?.speech_tone || 'N/A');
  const displayCurrentDuration = isCreator ? editableDuration : ((speech as any).current_version?.estimated_duration_minutes || 'N/A');
  const displayCurrentDraft = isCreator ? editableDraft : "Draft not available for viewing.";


  return (
    <VStack spacing={5} align="stretch" p={5}>
      <Box p={4} borderWidth="1px" borderRadius="md" shadow="sm">
        <Heading as="h1" size="lg" mb={3}>
          {/* Creator name not available on SecretSpeechPublic, use ID */}
          Speech by User {speech.creator_id.substring(0,8)}...
        </Heading>
        <Text><strong>Event Link:</strong> <RouterLink to={`/_layout/events/${speech.event_id}`}><Text as="span" color="blue.500" _hover={{textDecoration: "underline"}}>View Event</Text></RouterLink></Text>
        <Text><strong>Created by:</strong> {speech.creator_id} {isCreator && <Tag size="sm" colorScheme="green" ml={2}>Me</Tag>}</Text>
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
            {/* If no current_version_id, or if current_version details are still loading/missing */}
            {!speech.current_version_id && !isLoadingCurrentVersion && <Text>No current version set for this speech. Create one by saving changes.</Text>}
            {(isLoadingCurrentVersion && speech.current_version_id) && <Spinner label="Loading current version details..."/>}

            {/* Display/Edit area */}
            {/* This relies on editableXXX states being correctly populated by useEffect after speech/currentVersionDetails load */}
            <VStack spacing={4} align="stretch">
              <FormControl id="speech-tone-display" isReadOnly={!isCreator}>
                <FormLabel>Speech Tone</FormLabel>
                {isCreator ? (
                  <Select value={editableTone} onChange={(e) => setEditableTone(e.target.value)} isDisabled={createVersionMutation.isPending}>
                    {speechTones.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                  </Select>
                ) : (
                  <Text>{displayCurrentTone}</Text>
                )}
              </FormControl>

              <FormControl id="speech-duration-display" isReadOnly={!isCreator}>
                <FormLabel>Estimated Duration (minutes)</FormLabel>
                {isCreator ? (
                  <NumberInput
                      min={1}
                      value={editableDuration}
                      onChange={(valStr) => setEditableDuration(valStr ? parseInt(valStr) : '')}
                      isDisabled={createVersionMutation.isPending}
                  >
                    <NumberInputField />
                    <NumberInputStepper><NumberIncrementStepper /><NumberDecrementStepper /></NumberInputStepper>
                  </NumberInput>
                ) : (
                  <Text>{displayCurrentDuration} minutes</Text>
                )}
              </FormControl>

              <FormControl id="speech-draft-display" isReadOnly={!isCreator}>
                <FormLabel>Speech Draft</FormLabel>
                {isCreator ? (
                  <Textarea
                    value={editableDraft}
                    onChange={(e) => setEditableDraft(e.target.value)}
                    rows={15}
                    placeholder="Write your speech draft here..."
                    isDisabled={createVersionMutation.isPending}
                  />
                ) : (
                  <Text whiteSpace="pre-wrap" fontFamily="monospace" p={2} borderWidth="1px" borderRadius="md" bg="gray.50" minH="100px">
                    {displayCurrentDraft}
                  </Text>
                )}
              </FormControl>

              {isCreator && (
                <Button colorScheme="teal" onClick={handleSaveChanges} isLoading={createVersionMutation.isPending} loadingText="Saving...">
                  Save Changes (Creates New Version)
                </Button>
              )}
            </VStack>
          </TabPanel>
          <TabPanel>
            <SpeechVersionHistory
              speechId={speech.id}
              currentUserId={currentUserId}
              isCreator={isCreator}
              currentSpeechVersionId={speech.current_version_id}
              onVersionSetAsCurrent={handleVersionSetAsCurrent}
            />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </VStack>
  );
};

export default SpeechDetailPage;
