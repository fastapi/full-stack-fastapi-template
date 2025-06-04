import { createFileRoute, useParams } from '@tanstack/react-router';
import EventDetailPage from '../../../components/Events/EventDetailPage'; // Adjust path as needed
import { Text } from '@chakra-ui/react';

export const Route = createFileRoute('/_layout/events/$eventId')({
  component: EventDetailPageWrapper,
  // Example of a loader to fetch data, though component itself also fetches
  // loader: async ({ params }) => fetchEventById(params.eventId),
});

// Wrapper component to potentially handle loading/error states from loader if used,
// or just to pass params if the component handles its own data fetching.
function EventDetailPageWrapper() {
  const { eventId } = useParams({ from: '/_layout/events/$eventId' });

  if (!eventId) {
    // This check might be redundant if the route matching requires eventId,
    // but good for robustness or if params are somehow optional/undefined.
    return <Text>Error: Event ID is missing.</Text>;
  }
  // EventDetailPage component already handles its own data fetching and params via its own useParams call.
  // So, we just render it.
  return <EventDetailPage />;
}
