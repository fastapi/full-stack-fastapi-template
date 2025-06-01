import React, { useState, useCallback } from 'react';
import {
  Box,
  Button,
  VStack,
  List,
  ListItem,
  Text,
  Heading,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Tag,
  HStack,
  Icon,
} from '@chakra-ui/react';
import { InfoIcon, WarningIcon, CheckCircleIcon, QuestionOutlineIcon } from '@chakra-ui/icons'; // Example icons
// import { EventsService, PersonalizedNudgePublic as ApiNudge } from '../../client'; // Step 7
import { mockNudges as globalMockNudges, PersonalizedNudgePublic } from '../../mocks/mockData'; // Import mock nudges


interface SpeechAnalysisDisplayProps {
  eventId: string;
}

// NudgeSeverityIcon and NudgeSeverityColorScheme can remain as they are, or be moved to a utils file if preferred.
const NudgeSeverityIcon: React.FC<{ severity: string }> = ({ severity }) => {
  switch (severity.toLowerCase()) {
    case 'warning':
      return <WarningIcon color="orange.500" />;
    case 'info':
      return <InfoIcon color="blue.500" />;
    case 'suggestion':
      return <QuestionOutlineIcon color="purple.500" />
    default:
      return <CheckCircleIcon color="green.500" />; // Default or for "success" like severities
  }
};

const NudgeSeverityColorScheme = (severity: string): string => {
    switch (severity.toLowerCase()) {
        case 'warning': return 'orange';
        case 'info': return 'blue';
        case 'suggestion': return 'purple';
        default: return 'gray';
    }
}

const SpeechAnalysisDisplay: React.FC<SpeechAnalysisDisplayProps> = ({ eventId }) => {
  const [nudges, setNudges] = useState<PersonalizedNudgePublic[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasAnalyzed, setHasAnalyzed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // const { user } = useAuth(); // To pass currentUserId if backend needs it for filtering (though plan is backend filters)

  const handleFetchAnalysis = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setHasAnalyzed(true);
    try {
      console.log(`SpeechAnalysisDisplay: Fetching analysis for event ${eventId}`);
      // const fetchedNudges = await EventsService.getEventSpeechAnalysis({ eventId }); // Step 7
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API call

      // Backend is expected to filter nudges for the current user.
      // So, for mock, we just return all globalMockNudges if the eventId is one we have speeches for.
      // A more sophisticated mock might check if currentUserId has speeches in that event.
      if (eventId === 'event-001-wedding' || eventId === 'event-002-techconf') {
        setNudges(globalMockNudges);
      } else if (eventId === 'event-003-bookclub') { // Event with no speeches initially, or different user
        setNudges([]); // No nudges for this event or user
      }
       else {
        // For other eventIds in mock, or if we want to simulate an error for specific event
        // throw new Error("Mock: Analysis data not available for this specific event.");
        setNudges([]); // Default to no nudges for unknown mock events
      }

    } catch (err) {
      console.error(`Failed to fetch speech analysis for event ${eventId}:`, err);
      const errorMessage = (err instanceof Error) ? err.message : 'An unknown error occurred.';
      setError(`Failed to load analysis (mock). ${errorMessage}`);
      setNudges([]); // Clear previous nudges on error
    } finally {
      setIsLoading(false);
    }
  }, [eventId]);

  return (
    <Box p={4} borderWidth="1px" borderRadius="lg" shadow="base">
      <Heading size="md" mb={4}>
        Personalized Speech Suggestions
      </Heading>
      <VStack spacing={4} align="stretch">
        <Button
          onClick={handleFetchAnalysis}
          isLoading={isLoading}
          loadingText="Analyzing..."
          colorScheme="blue"
          disabled={isLoading}
        >
          {hasAnalyzed ? 'Refresh Suggestions' : 'Get Personalized Suggestions'}
        </Button>

        {isLoading && (
          <Box textAlign="center" p={5}>
            <Spinner size="lg" />
            <Text mt={2}>Generating your suggestions...</Text>
          </Box>
        )}

        {!isLoading && error && (
          <Alert status="error">
            <AlertIcon />
            <AlertTitle>Error Fetching Analysis!</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {!isLoading && !error && hasAnalyzed && nudges.length === 0 && (
          <Alert status="info">
            <AlertIcon />
            <AlertTitle>No Specific Nudges!</AlertTitle>
            <AlertDescription>No specific suggestions for you at this moment, or all speeches align well!</AlertDescription>
          </Alert>
        )}

        {!isLoading && !error && nudges.length > 0 && (
          <List spacing={3}>
            {nudges.map((nudge, index) => (
              <ListItem key={index} p={3} borderWidth="1px" borderRadius="md" bg="gray.50">
                <HStack spacing={3} align="start">
                  <Icon as={() => <NudgeSeverityIcon severity={nudge.severity} />} w={5} h={5} mt={1} />
                  <Box>
                    <Tag size="sm" colorScheme={NudgeSeverityColorScheme(nudge.severity)} mb={1}>
                      {nudge.nudge_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Tag>
                    <Text fontSize="sm">{nudge.message}</Text>
                  </Box>
                </HStack>
              </ListItem>
            ))}
          </List>
        )}
      </VStack>
    </Box>
  );
};

export default SpeechAnalysisDisplay;
