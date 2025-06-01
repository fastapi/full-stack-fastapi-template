import { createFileRoute } from '@tanstack/react-router';
import EventCreateForm from '../../../components/Events/EventCreateForm'; // Adjust path as needed

export const Route = createFileRoute('/_layout/events/create')({
  component: EventCreatePage,
});

function EventCreatePage() {
  // Optional: Add a breadcrumb or heading specific to this page if needed
  return <EventCreateForm />;
}
