import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { apiService, WorkoutPostResponse, WorkoutPostsResponse, WorkoutPostCreateRequest } from '../services/api';

export type FeedType = 'personal' | 'public' | 'combined';

interface FeedState {
  personalFeed: WorkoutPostResponse[];
  publicFeed: WorkoutPostResponse[];
  combinedFeed: WorkoutPostResponse[];
  isLoading: boolean;
  error: string | null;
  hasMore: boolean;
  currentFeedType: FeedType;
}

interface FeedContextType extends FeedState {
  // Feed operations
  loadFeed: (feedType: FeedType, refresh?: boolean) => Promise<void>;
  loadMorePosts: () => Promise<void>;
  refreshFeed: () => Promise<void>;
  setCurrentFeedType: (feedType: FeedType) => void;
  
  // Post operations
  createPost: (postData: WorkoutPostCreateRequest) => Promise<void>;
  deletePost: (postId: string) => Promise<void>;
  
  // Utility functions
  getCurrentFeed: () => WorkoutPostResponse[];
  clearError: () => void;
}

const FeedContext = createContext<FeedContextType | undefined>(undefined);

interface FeedProviderProps {
  children: ReactNode;
}

export function FeedProvider({ children }: FeedProviderProps) {
  const [state, setState] = useState<FeedState>({
    personalFeed: [],
    publicFeed: [],
    combinedFeed: [],
    isLoading: false,
    error: null,
    hasMore: true,
    currentFeedType: 'personal',
  });

  const setLoading = useCallback((isLoading: boolean) => {
    setState(prev => ({ ...prev, isLoading }));
  }, []);

  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error }));
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, [setError]);

  const setCurrentFeedType = useCallback((feedType: FeedType) => {
    setState(prev => ({ ...prev, currentFeedType: feedType }));
  }, []);

  const getCurrentFeedForType = useCallback((feedType: FeedType): WorkoutPostResponse[] => {
    switch (feedType) {
      case 'personal':
        return state.personalFeed;
      case 'public':
        return state.publicFeed;
      case 'combined':
        return state.combinedFeed;
      default:
        return state.personalFeed;
    }
  }, [state.personalFeed, state.publicFeed, state.combinedFeed]);

  const getCurrentFeed = useCallback((): WorkoutPostResponse[] => {
    switch (state.currentFeedType) {
      case 'personal':
        return state.personalFeed;
      case 'public':
        return state.publicFeed;
      case 'combined':
        return state.combinedFeed;
      default:
        return state.personalFeed;
    }
  }, [state.personalFeed, state.publicFeed, state.combinedFeed, state.currentFeedType]);

  const loadFeed = useCallback(async (feedType: FeedType, refresh: boolean = false) => {
    try {
      setLoading(true);
      setError(null);

      const currentFeed = getCurrentFeedForType(feedType);
      const skip = refresh ? 0 : currentFeed.length;
      
      let response: WorkoutPostsResponse;
      
      switch (feedType) {
        case 'personal':
          response = await apiService.getPersonalFeed(skip, 20);
          break;
        case 'public':
          response = await apiService.getPublicFeed(skip, 20);
          break;
        case 'combined':
          response = await apiService.getFeed('combined', skip, 20);
          break;
        default:
          response = await apiService.getPersonalFeed(skip, 20);
      }

      setState(prev => {
        const newState = { ...prev };
        const feedKey = `${feedType}Feed` as keyof Pick<FeedState, 'personalFeed' | 'publicFeed' | 'combinedFeed'>;
        
        if (refresh) {
          newState[feedKey] = response.data;
        } else {
          newState[feedKey] = [...prev[feedKey], ...response.data];
        }
        
        newState.hasMore = response.data.length === 20; // Assume no more if less than requested
        return newState;
      });
    } catch (error) {
      console.error('Error loading feed:', error);
      setError(error instanceof Error ? error.message : 'Failed to load feed');
    } finally {
      setLoading(false);
    }
  }, [getCurrentFeedForType, setLoading, setError]);

  const loadMorePosts = useCallback(async () => {
    if (!state.hasMore || state.isLoading) return;
    await loadFeed(state.currentFeedType, false);
  }, [state.hasMore, state.isLoading, state.currentFeedType, loadFeed]);

  const refreshFeed = useCallback(async () => {
    await loadFeed(state.currentFeedType, true);
  }, [state.currentFeedType, loadFeed]);

  const createPost = useCallback(async (postData: WorkoutPostCreateRequest) => {
    try {
      setLoading(true);
      setError(null);

      const newPost = await apiService.createWorkoutPost(postData);
      
      // Add the new post to the beginning of relevant feeds
      setState(prev => ({
        ...prev,
        personalFeed: [newPost, ...prev.personalFeed],
        combinedFeed: [newPost, ...prev.combinedFeed],
        // Add to public feed only if it's a public post
        publicFeed: newPost.is_public ? [newPost, ...prev.publicFeed] : prev.publicFeed,
      }));
    } catch (error) {
      console.error('Error creating post:', error);
      setError(error instanceof Error ? error.message : 'Failed to create post');
      throw error; // Re-throw so the UI can handle it
    } finally {
      setLoading(false);
    }
  }, []);

  const deletePost = useCallback(async (postId: string) => {
    try {
      setLoading(true);
      setError(null);

      await apiService.deleteWorkoutPost(postId);
      
      // Remove the post from all feeds
      setState(prev => ({
        ...prev,
        personalFeed: prev.personalFeed.filter(post => post.id !== postId),
        publicFeed: prev.publicFeed.filter(post => post.id !== postId),
        combinedFeed: prev.combinedFeed.filter(post => post.id !== postId),
      }));
    } catch (error) {
      console.error('Error deleting post:', error);
      setError(error instanceof Error ? error.message : 'Failed to delete post');
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const contextValue: FeedContextType = {
    ...state,
    loadFeed,
    loadMorePosts,
    refreshFeed,
    setCurrentFeedType,
    createPost,
    deletePost,
    getCurrentFeed,
    clearError,
  };

  return (
    <FeedContext.Provider value={contextValue}>
      {children}
    </FeedContext.Provider>
  );
}

export function useFeed() {
  const context = useContext(FeedContext);
  if (context === undefined) {
    throw new Error('useFeed must be used within a FeedProvider');
  }
  return context;
}