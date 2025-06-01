import { createFileRoute, useParams } from '@tanstack/react-router';
import SpeechDetailPage from '../../../components/Speeches/SpeechDetailPage'; // Adjust path as needed
import { Text } from '@chakra-ui/react';

export const Route = createFileRoute('/_layout/speeches/$speechId')({
  component: SpeechDetailPageWrapper,
  // loader: async ({ params }) => fetchSpeechById(params.speechId), // Example loader
});

function SpeechDetailPageWrapper() {
  const { speechId } = useParams({ from: '/_layout/speeches/$speechId' });

  if (!speechId) {
    return <Text>Error: Speech ID is missing.</Text>;
  }
  // SpeechDetailPage component handles its own data fetching and param extraction.
  return <SpeechDetailPage />;
}
