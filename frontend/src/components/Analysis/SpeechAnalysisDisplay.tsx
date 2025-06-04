import React, { useState } from 'react'; // Removed useCallback
import { useQuery } from '@tanstack/react-query';
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
import { InfoIcon, WarningIcon, CheckCircleIcon, QuestionOutlineIcon } from '@chakra-ui/icons';
import { EventsService, PersonalizedNudgePublic, ApiError } from '../../../client';

interface SpeechAnalysisDisplayProps {
  eventId: string;
}

const NudgeSeverityIcon: React.FC<{ severity: string }> = ({ severity }) => {
  switch (severity.toLowerCase()) {
    case 'warning':
      return <WarningIcon color="orange.500" />;
    case 'info':
      return <InfoIcon color="blue.500" />;
    case 'suggestion':
      return <QuestionOutlineIcon color="purple.500" />
    default:
      return <CheckCircleIcon color="green.500" />;
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
  const [hasAnalyzed, setHasAnalyzed] = useState(false);

  const {
    data: nudges,
    isFetching,
    isError,
    error,
    refetch
  } = useQuery<PersonalizedNudgePublic[], ApiError>({
    queryKey: ['speechAnalysis', eventId],
    queryFn: async () => {
      if (!eventId) throw new Error("Event ID is required for analysis.");
      return EventsService.getEventSpeechAnalysis({ eventId });
    },
    enabled: false,
  });

  const handleFetchAnalysisClick = () => {
    setHasAnalyzed(true);
    refetch();
  };

  return (
    <Box p={4} borderWidth="1px" borderRadius="lg" shadow="base">
      <Heading size="md" mb={4}>
        Personalized Speech Suggestions
      </Heading>
      <VStack spacing={4} align="stretch">
        <Button
          onClick={handleFetchAnalysisClick}
          isLoading={isFetching}
          loadingText="Analyzing..."
          colorScheme="blue"
          disabled={isFetching}
        >
          {hasAnalyzed && !isFetching ? 'Refresh Suggestions' : 'Get Personalized Suggestions'}
        </Button>

        {isFetching && (
          <Box textAlign="center" p={5}>
            <Spinner size="lg" />
            <Text mt={2}>Generating your suggestions...</Text>
          </Box>
        )}

        {!isFetching && isError && (
          <Alert status="error" mt={4} variant="subtle" flexDirection="column" alignItems="center" justifyContent="center" textAlign="center" minHeight="150px">
            <AlertIcon boxSize="30px" mr={0} />
            <AlertTitle mt={3} mb={1} fontSize="md">Error Fetching Analysis!</AlertTitle>
            <AlertDescription maxWidth="sm" fontSize="sm">{error?.body?.detail || error?.message || 'An unexpected error occurred.'}</AlertDescription>
          </Alert>
        )}

        {!isFetching && !isError && hasAnalyzed && (!nudges || nudges.length === 0) && (
          <Alert status="info" mt={4} variant="subtle" flexDirection="column" alignItems="center" justifyContent="center" textAlign="center" minHeight="150px">
            <AlertIcon boxSize="30px" mr={0} />
            <AlertTitle mt={3} mb={1} fontSize="md">No Specific Nudges!</AlertTitle>
            <AlertDescription maxWidth="sm" fontSize="sm">No specific suggestions for you at this moment, or all speeches align well!</AlertDescription>
          </Alert>
        )}

        {!isFetching && !isError && nudges && nudges.length > 0 && (
          <List spacing={3}>
            {nudges.map((nudge, index) => (
              <ListItem key={index} p={3} borderWidth="1px" borderRadius="md" bg="gray.50" _hover={{ bg: 'gray.100' }}>
                <HStack spacing={3} align="start">
                  <Icon as={() => <NudgeSeverityIcon severity={nudge.severity} />} w={6} h={6} mt={1} />
                  <Box>
                    <Tag size="md" colorScheme={NudgeSeverityColorScheme(nudge.severity)} mb={1} variant="subtle">
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
