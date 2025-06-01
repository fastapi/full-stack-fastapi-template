import React, { useState } from 'react';
import {
  Button,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  VStack,
  Heading,
  useToast,
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Box,
} from '@chakra-ui/react';
// import { SpeechesService, SecretSpeechWithInitialVersionCreate as ApiSpeechCreate } from '../../client'; // Step 7
import {
    addMockSpeech,
    currentUserId,
    mockUserAlice,
    SecretSpeechPublicDetailed, // For constructing the object to add
    SecretSpeechVersionData,  // For constructing the initial version
} from '../../mocks/mockData'; // Import mock function and user

// Placeholder interface for the data this form collects (matches backend Pydantic model)
interface SpeechCreateFormPayload {
  initial_speech_draft: string;
  initial_speech_tone: string;
  initial_estimated_duration_minutes: number;
}

const speechTones = ["neutral", "sentimental", "humorous", "serious", "inspirational", "mixed", "other"];

interface SpeechCreateFormProps {
  eventId: string;
  onSpeechCreated?: () => void; // Optional callback to refresh list or close modal
}

const SpeechCreateForm: React.FC<SpeechCreateFormProps> = ({ eventId, onSpeechCreated }) => {
  const [draft, setDraft] = useState('');
  const [tone, setTone] = useState(speechTones[0]);
  const [duration, setDuration] = useState<number | string>(5); // Can be string if input is empty
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();
  // const { user } = useAuth();
  // const actualCreatorId = user?.id || currentUserId;
  const actualCreatorId = currentUserId; // From mockData
  const actualCreatorName = mockUserAlice.full_name; // Assuming Alice is current user

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    if (!draft.trim() || !tone || duration === '' || Number(duration) <= 0) {
      toast({
        title: 'Missing or invalid fields',
        description: 'Draft, Tone, and a valid Duration are required.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setIsLoading(false);
      return;
    }

    // This is what would be sent to the backend API
    const apiPayload = {
      event_id: eventId,
      initial_speech_draft: draft,
      initial_speech_tone: tone,
      initial_estimated_duration_minutes: Number(duration)
    };
    console.log('Simulating API submission with payload:', apiPayload);

    try {
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call

      // For mock data update, construct the full SecretSpeechPublicDetailed object
      const newSpeechId = `speech-mock-${Date.now()}`;
      const newVersionId = `v-mock-${newSpeechId}-1`;

      const initialVersion: SecretSpeechVersionData = {
        id: newVersionId,
        version_number: 1,
        speech_id: newSpeechId, // Link back to speech
        speech_draft: draft,
        speech_tone: tone,
        estimated_duration_minutes: Number(duration),
        created_at: new Date().toISOString(),
        creator_id: actualCreatorId,
      };

      const newSpeech: SecretSpeechPublicDetailed = {
        id: newSpeechId,
        event_id: eventId,
        creator_id: actualCreatorId,
        creator_name: actualCreatorName,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        current_version_id: newVersionId,
        current_version: initialVersion,
      };

      addMockSpeech(newSpeech); // Add to the shared mock data array

      toast({
        title: 'Speech Created (Mock)',
        description: 'Your new speech has been successfully created.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      setDraft('');
      setTone(speechTones[0]);
      setDuration(5);
      if (onSpeechCreated) {
        onSpeechCreated();
      }
    } catch (error) {
      console.error('Failed to create speech:', error);
      toast({
        title: 'Creation Failed',
        description: 'There was an error creating the speech. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box p={4} borderWidth="1px" borderRadius="lg" shadow="md">
      <VStack spacing={4} as="form" onSubmit={handleSubmit} w="100%">
        <Heading as="h3" size="md" textAlign="center">
          Add New Speech to Event
        </Heading>
        <FormControl id="speech-draft" isRequired>
          <FormLabel>Initial Speech Draft</FormLabel>
          <Textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Write your speech draft here..."
            rows={8}
          />
        </FormControl>

        <FormControl id="speech-tone" isRequired>
          <FormLabel>Initial Speech Tone</FormLabel>
          <Select value={tone} onChange={(e) => setTone(e.target.value)}>
            {speechTones.map(t => (
              <option key={t} value={t}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </option>
            ))}
          </Select>
        </FormControl>

        <FormControl id="speech-duration" isRequired>
          <FormLabel>Estimated Duration (minutes)</FormLabel>
          <NumberInput
            min={1}
            value={duration}
            onChange={(valueString) => setDuration(valueString ? parseInt(valueString) : '')}
          >
            <NumberInputField placeholder="e.g., 5" />
            <NumberInputStepper>
              <NumberIncrementStepper />
              <NumberDecrementStepper />
            </NumberInputStepper>
          </NumberInput>
        </FormControl>

        <Button
          type="submit"
          colorScheme="teal"
          isLoading={isLoading}
          loadingText="Saving..."
          w="100%"
        >
          Create Speech
        </Button>
      </VStack>
    </Box>
  );
};

export default SpeechCreateForm;
