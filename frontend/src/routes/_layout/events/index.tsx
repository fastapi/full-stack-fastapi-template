import { createFileRoute } from '@tanstack/react-router';
import EventList from '../../../components/Events/EventList'; // Adjust path as needed

export const Route = createFileRoute('/_layout/events/')({
  component: EventsIndexPage,
});

function EventsIndexPage() {
  return <EventList />;
}
