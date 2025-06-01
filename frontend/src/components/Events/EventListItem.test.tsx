import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ChakraProvider } from '@chakra-ui/react';
import EventListItem from './EventListItem';
import { CoordinationEventPublic } from '../../client'; // Import the correct type

// Mock @tanstack/react-router's Link component
vi.mock('@tanstack/react-router', () => ({
  Link: vi.fn(({ to, children, ...rest }) => <a href={to} {...rest}>{children}</a>),
}));

const renderWithChakraProvider = (ui: React.ReactElement) => {
  return render(<ChakraProvider>{ui}</ChakraProvider>);
};

const mockEvent: CoordinationEventPublic = {
  id: 'event-123',
  event_name: 'Community Tech Talk',
  event_type: 'tech_talk',
  event_date: '2024-09-15T10:00:00.000Z', // ISO string
  creator_id: 'user-abc',
  created_at: '2024-07-01T10:00:00.000Z',
  updated_at: '2024-07-02T12:00:00.000Z',
};

const mockEventNoDate: CoordinationEventPublic = {
    id: 'event-456',
    event_name: 'Planning Meeting',
    event_type: 'meeting',
    // event_date is optional in some definitions, but CoordinationEventPublic from client requires it.
    // Let's assume the client type requires it as a string, so we should provide a valid or empty string
    // if the backend can send it as null/undefined and client maps to string.
    // For the client type `CoordinationEventPublic`, `event_date: string`.
    // If the backend guarantees a string (even if empty for no date), that's fine.
    // If it can be truly null/undefined from backend, client type should be `string | null | undefined`.
    // Assuming here backend sends a valid date string, or this test would need adjustment based on actual client type nullability.
    event_date: new Date(2023, 5, 10).toISOString(), // Example past date if required
    creator_id: 'user-def',
    created_at: '2023-05-01T10:00:00.000Z',
    updated_at: '2023-05-01T12:00:00.000Z',
  };


describe('EventListItem', () => {
  it('renders event details correctly', () => {
    renderWithChakraProvider(<EventListItem event={mockEvent} />);

    expect(screen.getByText(mockEvent.event_name)).toBeInTheDocument();
    // Test formatted type: 'Tech Talk'
    expect(screen.getByText(/type: Tech Talk/i)).toBeInTheDocument();
    // Test formatted date
    // Date formatting can be tricky due to locales. Check for parts of it.
    // For '2024-09-15T10:00:00.000Z', toLocaleDateString might give "September 15, 2024" in en-US
    expect(screen.getByText(/Date: September 15, 2024/i)).toBeInTheDocument();
    expect(screen.getByText(/Event ID: event-123/i)).toBeInTheDocument();
  });

  it('renders "Date not set" if event_date is missing or unparseable (if type allowed optional/null)', () => {
    // To properly test this, CoordinationEventPublic event_date type should be string | null | undefined
    // And the component's formatDate should handle it.
    // Given current client type `event_date: string`, backend must send a string.
    // If backend sent an empty string for "no date":
    const eventWithEmptyDate = { ...mockEvent, event_date: '' };
    renderWithChakraProvider(<EventListItem event={eventWithEmptyDate} />);
    expect(screen.getByText(/Date: Date not set/i)).toBeInTheDocument();
  });

  it('renders "Invalid date" if event_date is unparseable', () => {
    const eventWithInvalidDate = { ...mockEvent, event_date: 'invalid-date-string' };
    renderWithChakraProvider(<EventListItem event={eventWithInvalidDate} />);
    expect(screen.getByText(/Date: Invalid date/i)).toBeInTheDocument();
  });

  it('links to the correct event detail page', () => {
    renderWithChakraProvider(<EventListItem event={mockEvent} />);
    const linkElement = screen.getByRole('link', { name: mockEvent.event_name });
    expect(linkElement).toHaveAttribute('href', `/_layout/events/${mockEvent.id}`);
  });
});
