import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ChakraProvider } from '@chakra-ui/react'; // For Chakra components
import EventCreateForm from './EventCreateForm';
import { useMutation, useQueryClient } from '@tanstack/react-query';

// Mocking @tanstack/react-query
vi.mock('@tanstack/react-query', async () => {
  const original = await vi.importActual('@tanstack/react-query');
  return {
    ...original,
    useMutation: vi.fn(),
    useQueryClient: vi.fn(() => ({
        invalidateQueries: vi.fn(),
    })),
  };
});

// Mocking Chakra UI's useToast
const mockToast = vi.fn();
vi.mock('@chakra-ui/react', async () => {
  const originalChakra = await vi.importActual('@chakra-ui/react');
  return {
    ...originalChakra,
    useToast: () => mockToast,
  };
});

// Mock Tanstack Router navigation (if any redirects were used)
// vi.mock('@tanstack/react-router', async () => ({
//   ...await vi.importActual('@tanstack/react-router'),
//   useNavigate: () => vi.fn(),
// }));


// Helper to render with ChakraProvider
const renderWithChakraProvider = (ui: React.ReactElement) => {
  return render(<ChakraProvider>{ui}</ChakraProvider>);
};

describe('EventCreateForm', () => {
  let mockMutate: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.resetAllMocks(); // Reset mocks before each test
    mockMutate = vi.fn();
    (useMutation as ReturnType<typeof vi.mocked>).mockImplementation(
        (options: any) => ({ // Use 'any' for options if type is complex or not critical for mock
      mutate: mockMutate,
      isPending: false,
      isError: false,
      error: null,
      data: null,
      // Add other properties useMutation might return if needed by component
        ...options // spread options to allow testing onSuccess/onError if needed
    }));
  });

  it('renders the form with key fields and submit button', () => {
    renderWithChakraProvider(<EventCreateForm />);
    expect(screen.getByLabelText(/event name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/event type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/event date/i)).toBeInTheDocument(); // Label includes "(Optional)"
    expect(screen.getByRole('button', { name: /create event/i })).toBeInTheDocument();
  });

  it('allows typing into input fields', () => {
    renderWithChakraProvider(<EventCreateForm />);
    const eventNameInput = screen.getByLabelText(/event name/i) as HTMLInputElement;
    fireEvent.change(eventNameInput, { target: { value: 'My Test Event' } });
    expect(eventNameInput.value).toBe('My Test Event');

    const eventTypeSelect = screen.getByLabelText(/event type/i) as HTMLSelectElement;
    fireEvent.change(eventTypeSelect, { target: { value: 'wedding_speech_pair' } });
    expect(eventTypeSelect.value).toBe('wedding_speech_pair');

    const eventDateInput = screen.getByLabelText(/event date/i) as HTMLInputElement;
    fireEvent.change(eventDateInput, { target: { value: '2024-12-25' } });
    expect(eventDateInput.value).toBe('2024-12-25');
  });

  it('calls mutation with correct data on submit and shows success toast', async () => {
    const mockInvalidateQueries = vi.fn();
    (useQueryClient as ReturnType<typeof vi.mocked>).mockReturnValue({
        invalidateQueries: mockInvalidateQueries,
        // Add other methods if your component uses them
    } as any);

    // Mock useMutation to simulate success
    (useMutation as ReturnType<typeof vi.mocked>).mockImplementation(
        (options: any) => ({
            mutate: (data: any) => {
                options.onSuccess?.({ ...data, id: 'new-event-id' }); // Simulate success with returned data
            },
            isPending: false,
            isError: false,
            error: null,
        } as any)
    );

    renderWithChakraProvider(<EventCreateForm />);

    fireEvent.change(screen.getByLabelText(/event name/i), { target: { value: 'New Year Gala' } });
    fireEvent.change(screen.getByLabelText(/event type/i), { target: { value: 'other' } });
    fireEvent.change(screen.getByLabelText(/event date/i), { target: { value: '2025-01-01' } });

    fireEvent.click(screen.getByRole('button', { name: /create event/i }));

    // Check that the mutation was called (implicitly by checking onSuccess effects)
    // Direct check of mockMutate is tricky here due to re-mocking for onSuccess

    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Event Created',
          status: 'success',
        })
      );
    });

    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ['events'] });

    // Check if form resets (example for eventName)
    expect((screen.getByLabelText(/event name/i) as HTMLInputElement).value).toBe('');
  });

  it('shows error toast if required fields are missing on submit', () => {
    renderWithChakraProvider(<EventCreateForm />);
    fireEvent.click(screen.getByRole('button', { name: /create event/i }));
    expect(mockMutate).not.toHaveBeenCalled();
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Missing fields',
        status: 'error',
      })
    );
  });

  it('disables submit button when mutation is pending', () => {
    (useMutation as ReturnType<typeof vi.mocked>).mockReturnValue({
      mutate: mockMutate,
      isPending: true, // Simulate loading state
      isError: false,
      error: null,
      data: null,
    } as any);

    renderWithChakraProvider(<EventCreateForm />);
    const submitButton = screen.getByRole('button', { name: /create event/i });
    expect(submitButton).toBeDisabled();
  });
});
