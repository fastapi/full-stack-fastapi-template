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
import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Button,
  FormControl,
  FormLabel,
  Input, // Keep if needed, but duration uses NumberInput
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
import { SpeechesService, SecretSpeechWithInitialVersionCreate, SecretSpeechPublic, ApiError } from '../../../client';
// import { useAuth } from '../../../hooks/useAuth'; // For creator_id if not handled by backend

const speechTones = ["neutral", "sentimental", "humorous", "serious", "inspirational", "mixed", "other"];

interface SpeechCreateFormProps {
  eventId: string;
  onSpeechCreated?: () => void;
}

const SpeechCreateForm: React.FC<SpeechCreateFormProps> = ({ eventId, onSpeechCreated }) => {
  const queryClient = useQueryClient();
  const toast = useToast();
  // const { user } = useAuth(); // If creator_id needs to be sent explicitly from frontend

  const [draft, setDraft] = useState('');
  const [tone, setTone] = useState(speechTones[0]);
  const [duration, setDuration] = useState<number | string>(5);

  const mutation = useMutation<
    SecretSpeechPublic, // Expected response type
    ApiError,
    SecretSpeechWithInitialVersionCreate // Input type to mutationFn
  >({
    mutationFn: async (newSpeechData: SecretSpeechWithInitialVersionCreate) => {
      // SpeechesService.createSpeech expects SpeechesCreateSpeechData which has requestBody
      return SpeechesService.createSpeech({ requestBody: newSpeechData });
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['eventSpeeches', eventId] });
      toast({
        title: 'Speech Created',
        description: `Your speech has been successfully added to the event.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      setDraft('');
      setTone(speechTones[0]);
      setDuration(5);
      if (onSpeechCreated) {
        onSpeechCreated(); // Typically closes modal and might trigger other actions in parent
      }
    },
    onError: (error) => {
      toast({
        title: 'Creation Failed',
        description: error.body?.detail?.[0]?.msg || error.message || 'There was an error creating the speech.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!draft.trim() || !tone || duration === '' || Number(duration) <= 0) {
      toast({
        title: 'Missing or invalid fields',
        description: 'Draft, Tone, and a valid Duration are required.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    const speechPayload: SecretSpeechWithInitialVersionCreate = {
      event_id: eventId,
      initial_speech_draft: draft,
      initial_speech_tone: tone,
      initial_estimated_duration_minutes: Number(duration),
      // creator_id would be set by the backend based on the authenticated user
    };

    mutation.mutate(speechPayload);
  };

  return (
    <Box p={4} borderWidth="1px" borderRadius="lg" shadow="md">
      <VStack spacing={4} as="form" onSubmit={handleSubmit} w="100%">
        <Heading as="h3" size="md" textAlign="center">
          Add New Speech to Event
        </Heading>
        <FormControl id="speech-draft" isRequired isInvalid={!!mutation.error?.body?.detail?.find((e: any) => e.loc?.includes('initial_speech_draft'))}>
          <FormLabel>Initial Speech Draft</FormLabel>
          <Textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Write your speech draft here..."
            rows={8}
            isDisabled={mutation.isPending}
          />
        </FormControl>

        <FormControl id="speech-tone" isRequired isInvalid={!!mutation.error?.body?.detail?.find((e: any) => e.loc?.includes('initial_speech_tone'))}>
          <FormLabel>Initial Speech Tone</FormLabel>
          <Select
            value={tone}
            onChange={(e) => setTone(e.target.value)}
            isDisabled={mutation.isPending}
          >
            {speechTones.map(t => (
              <option key={t} value={t}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </option>
            ))}
          </Select>
        </FormControl>

        <FormControl id="speech-duration" isRequired isInvalid={!!mutation.error?.body?.detail?.find((e: any) => e.loc?.includes('initial_estimated_duration_minutes'))}>
          <FormLabel>Estimated Duration (minutes)</FormLabel>
          <NumberInput
            min={1}
            value={duration}
            onChange={(valueString) => setDuration(valueString ? parseInt(valueString) : '')}
            isDisabled={mutation.isPending}
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
          isLoading={mutation.isPending}
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
