import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ChakraProvider } from '@chakra-ui/react';
import SpeechAnalysisDisplay, { PersonalizedNudgePublic } from './SpeechAnalysisDisplay'; // Import type if needed for mock
import { useQuery } from '@tanstack/react-query';

// Mock @tanstack/react-query's useQuery
vi.mock('@tanstack/react-query', async () => {
    const original = await vi.importActual('@tanstack/react-query');
    return {
        ...original,
        useQuery: vi.fn(),
    };
});

// Mock Chakra UI's useToast (if used, though not directly in this component)
// const mockToast = vi.fn();
// vi.mock('@chakra-ui/react', async () => {
//   const originalChakra = await vi.importActual('@chakra-ui/react');
//   return {
//     ...originalChakra,
//     useToast: () => mockToast,
//   };
// });

const renderWithChakraProvider = (ui: React.ReactElement) => {
  return render(<ChakraProvider>{ui}</ChakraProvider>);
};

const mockNudgesData: PersonalizedNudgePublic[] = [
  { nudge_type: 'tone_tip', message: 'Consider a lighter tone.', severity: 'suggestion' },
  { nudge_type: 'length_warning', message: 'Your speech is too long.', severity: 'warning' },
];

describe('SpeechAnalysisDisplay', () => {
  const mockRefetch = vi.fn();

  beforeEach(() => {
    vi.resetAllMocks();
    // Default mock for useQuery
    (useQuery as ReturnType<typeof vi.mocked>).mockReturnValue({
      data: undefined,
      isFetching: false,
      isError: false,
      error: null,
      refetch: mockRefetch,
    } as any);
  });

  it('renders initial state with "Get Personalized Suggestions" button', () => {
    renderWithChakraProvider(<SpeechAnalysisDisplay eventId="event-1" />);
    expect(screen.getByRole('button', { name: /get personalized suggestions/i })).toBeInTheDocument();
    expect(screen.queryByText(/consider a lighter tone/i)).not.toBeInTheDocument(); // No nudges initially
  });

  it('calls refetch when the button is clicked', () => {
    renderWithChakraProvider(<SpeechAnalysisDisplay eventId="event-1" />);
    const analyzeButton = screen.getByRole('button', { name: /get personalized suggestions/i });
    fireEvent.click(analyzeButton);
    expect(mockRefetch).toHaveBeenCalledTimes(1);
  });

  it('displays loading spinner when isFetching is true', () => {
    (useQuery as ReturnType<typeof vi.mocked>).mockReturnValue({
      data: undefined,
      isFetching: true,
      isError: false,
      error: null,
      refetch: mockRefetch,
    } as any);
    renderWithChakraProvider(<SpeechAnalysisDisplay eventId="event-1" />);
    // Button might also be disabled or show loading text depending on its own isLoading prop
    expect(screen.getByText(/generating your suggestions.../i)).toBeInTheDocument();
    // Check for spinner role if available, or part of button's loading state
    expect(screen.getByRole('status')).toBeInTheDocument(); // Chakra's Spinner has role="status"
  });

  it('displays error message when isError is true', async () => {
    const testError = { message: 'Failed to fetch analysis' } as any; // Simulate ApiError structure if needed
     (useQuery as ReturnType<typeof vi.mocked>).mockReturnValue({
      data: undefined,
      isFetching: false,
      isError: true,
      error: testError,
      refetch: mockRefetch,
    } as any);
    // Simulate that analysis was attempted by clicking button, which sets hasAnalyzed
    renderWithChakraProvider(<SpeechAnalysisDisplay eventId="event-1" />);
    // To ensure the error message for "isError" is shown only after an attempt,
    // we need to simulate the button click that sets `hasAnalyzed` to true.
    // However, the component directly uses `isError` from `useQuery` now.
    // The button click sets `hasAnalyzed` to true, then calls `refetch`.
    // If `refetch` leads to `isError`, the message shows.
    // For this test, we can assume `hasAnalyzed` becomes true implicitly if isError is true after a fetch.
    // A more robust way is to click, then update mock, then check.
    // Simplified: If isError is true, and isFetching is false, error should show.

    // To properly test the state after a failed refetch:
    const analyzeButton = screen.getByRole('button', { name: /get personalized suggestions/i });
    fireEvent.click(analyzeButton); // This sets hasAnalyzed=true and calls refetch which returns the error state

    await waitFor(() => {
        expect(screen.getByText(/error fetching analysis!/i)).toBeInTheDocument();
        expect(screen.getByText(testError.message, { exact: false })).toBeInTheDocument();
    });
  });

  it('displays nudges when data is available', () => {
    (useQuery as ReturnType<typeof vi.mocked>).mockReturnValue({
      data: mockNudgesData,
      isFetching: false,
      isError: false,
      error: null,
      refetch: mockRefetch,
    } as any);
     // To show nudges, `hasAnalyzed` also needs to be true.
    renderWithChakraProvider(<SpeechAnalysisDisplay eventId="event-1" />);
    const analyzeButton = screen.getByRole('button', { name: /get personalized suggestions/i });
    fireEvent.click(analyzeButton); // Sets hasAnalyzed = true & triggers refetch (which returns data)

    waitFor(() => {
        expect(screen.getByText(/consider a lighter tone./i)).toBeInTheDocument();
        expect(screen.getByText(/your speech is too long./i)).toBeInTheDocument();
        expect(screen.getByText(/tone_tip/i, { selector: 'span.chakra-tag__label' })).toBeInTheDocument(); // Check tag text
    });
  });

  it('displays "no suggestions" message when data is an empty array after analysis', () => {
    (useQuery as ReturnType<typeof vi.mocked>).mockReturnValue({
      data: [],
      isFetching: false,
      isError: false,
      error: null,
      refetch: mockRefetch,
    } as any);
    renderWithChakraProvider(<SpeechAnalysisDisplay eventId="event-1" />);
    const analyzeButton = screen.getByRole('button', { name: /get personalized suggestions/i });
    fireEvent.click(analyzeButton); // Sets hasAnalyzed = true

    waitFor(() => {
        expect(screen.getByText(/no specific nudges!/i)).toBeInTheDocument();
    });
  });

  it('button text changes to "Refresh Suggestions" after first analysis attempt if not fetching', () => {
    renderWithChakraProvider(<SpeechAnalysisDisplay eventId="event-1" />);
    const analyzeButton = screen.getByRole('button', { name: /get personalized suggestions/i });
    fireEvent.click(analyzeButton); // Sets hasAnalyzed = true, triggers refetch
    // Assuming refetch completes and isFetching becomes false:
    // useQuery mock will return isFetching: false by default after this click if not overridden
    waitFor(() => {
        expect(screen.getByRole('button', { name: /refresh suggestions/i })).toBeInTheDocument();
    });
  });
});
