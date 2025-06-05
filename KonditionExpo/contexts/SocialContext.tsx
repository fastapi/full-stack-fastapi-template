import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { apiService, UserSearchResult, UserProfile, UserPublicExtended } from '../services/api';

type SocialContextType = {
  // Search state
  searchResults: UserSearchResult[];
  searchLoading: boolean;
  searchError: string | null;
  
  // Followers/Following state
  followers: UserSearchResult[];
  following: UserSearchResult[];
  followersLoading: boolean;
  followingLoading: boolean;
  followersError: string | null;
  followingError: string | null;
  
  // Follow action state
  followActionLoading: { [userId: string]: boolean };
  
  // Methods
  searchUsers: (query: string, skip?: number, limit?: number) => Promise<void>;
  clearSearchResults: () => void;
  followUser: (userId: string) => Promise<void>;
  unfollowUser: (userId: string) => Promise<void>;
  getFollowers: (skip?: number, limit?: number) => Promise<void>;
  getFollowing: (skip?: number, limit?: number) => Promise<void>;
  refreshFollowers: () => Promise<void>;
  refreshFollowing: () => Promise<void>;
  isFollowing: (userId: string) => Promise<boolean>;
  getUserProfile: (userId: string) => Promise<UserPublicExtended>;
};

const SocialContext = createContext<SocialContextType | undefined>(undefined);

export const SocialProvider = ({ children }: { children: ReactNode }) => {
  // Search state
  const [searchResults, setSearchResults] = useState<UserSearchResult[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  
  // Followers/Following state
  const [followers, setFollowers] = useState<UserSearchResult[]>([]);
  const [following, setFollowing] = useState<UserSearchResult[]>([]);
  const [followersLoading, setFollowersLoading] = useState(false);
  const [followingLoading, setFollowingLoading] = useState(false);
  const [followersError, setFollowersError] = useState<string | null>(null);
  const [followingError, setFollowingError] = useState<string | null>(null);
  
  // Follow action state
  const [followActionLoading, setFollowActionLoading] = useState<{ [userId: string]: boolean }>({});

  const searchUsers = useCallback(async (query: string, skip: number = 0, limit: number = 20) => {
    if (!query.trim()) {
      setSearchResults([]);
      setSearchLoading(false); // Ensure loading is false when clearing
      return;
    }

    try {
      setSearchLoading(true);
      setSearchError(null);
      
      const response = await apiService.searchUsers(query.trim(), skip, limit);
      
      if (skip === 0) {
        setSearchResults(response.data);
      } else {
        // Append for pagination
        setSearchResults(prev => [...prev, ...response.data]);
      }
    } catch (error) {
      console.error('Search users failed:', error);
      setSearchError(error instanceof Error ? error.message : 'Failed to search users');
      if (skip === 0) {
        setSearchResults([]);
      }
    } finally {
      setSearchLoading(false);
    }
  }, []);

  const clearSearchResults = useCallback(() => {
    setSearchResults([]);
    setSearchError(null);
    setSearchLoading(false); // Ensure loading is false when clearing
  }, []);

  const followUser = useCallback(async (userId: string) => {
    try {
      setFollowActionLoading(prev => ({ ...prev, [userId]: true }));
      
      await apiService.followUser(userId);
      
      // Update local state in search results and followers
      setSearchResults(prev =>
        prev.map(user =>
          user.id === userId
            ? {
                ...user,
                is_following: true,
                follower_count: user.follower_count + 1
              }
            : user
        )
      );
      
      setFollowers(prev =>
        prev.map(user =>
          user.id === userId
            ? {
                ...user,
                is_following: true
              }
            : user
        )
      );
      
      // Immediately refresh the following list to show the new user
      console.log('[SocialContext] Follow successful, refreshing following list...');
      try {
        setFollowingLoading(true);
        setFollowingError(null);
        
        const response = await apiService.getFollowing(0, 100);
        console.log(`[SocialContext] Refreshed following list:`, response.data.length, 'users');
        setFollowing(response.data);
      } catch (error) {
        console.error('Failed to refresh following list after follow:', error);
        setFollowingError(error instanceof Error ? error.message : 'Failed to refresh following list');
      } finally {
        setFollowingLoading(false);
      }
      
    } catch (error) {
      console.error('Follow user failed:', error);
      throw error;
    } finally {
      setFollowActionLoading(prev => ({ ...prev, [userId]: false }));
    }
  }, []);

  const unfollowUser = useCallback(async (userId: string) => {
    try {
      setFollowActionLoading(prev => ({ ...prev, [userId]: true }));
      
      await apiService.unfollowUser(userId);
      
      // Update local state in search results and followers
      setSearchResults(prev =>
        prev.map(user =>
          user.id === userId
            ? {
                ...user,
                is_following: false,
                follower_count: Math.max(0, user.follower_count - 1)
              }
            : user
        )
      );
      
      setFollowers(prev =>
        prev.map(user =>
          user.id === userId
            ? {
                ...user,
                is_following: false
              }
            : user
        )
      );
      
      // Remove user from following list immediately
      setFollowing(prev => prev.filter(user => user.id !== userId));
      
      console.log('[SocialContext] Unfollow successful, user removed from following list');
      
    } catch (error) {
      console.error('Unfollow user failed:', error);
      throw error;
    } finally {
      setFollowActionLoading(prev => ({ ...prev, [userId]: false }));
    }
  }, []);

  const getFollowers = useCallback(async (skip: number = 0, limit: number = 100) => {
    try {
      setFollowersLoading(true);
      setFollowersError(null);
      
      const response = await apiService.getFollowers(skip, limit);
      
      if (skip === 0) {
        setFollowers(response.data);
      } else {
        // Append for pagination
        setFollowers(prev => [...prev, ...response.data]);
      }
    } catch (error) {
      console.error('Get followers failed:', error);
      setFollowersError(error instanceof Error ? error.message : 'Failed to load followers');
      if (skip === 0) {
        setFollowers([]);
      }
    } finally {
      setFollowersLoading(false);
    }
  }, []);

  const getFollowing = useCallback(async (skip: number = 0, limit: number = 100) => {
    try {
      setFollowingLoading(true);
      setFollowingError(null);
      
      const response = await apiService.getFollowing(skip, limit);
      
      // Debug logging
      console.log(`[SocialContext] getFollowing response:`, response);
      console.log(`[SocialContext] Following users:`, response.data.map(u => ({
        name: u.full_name || u.email,
        is_following: u.is_following
      })));
      
      if (skip === 0) {
        setFollowing(response.data);
      } else {
        // Append for pagination
        setFollowing(prev => [...prev, ...response.data]);
      }
    } catch (error) {
      console.error('Get following failed:', error);
      setFollowingError(error instanceof Error ? error.message : 'Failed to load following');
      if (skip === 0) {
        setFollowing([]);
      }
    } finally {
      setFollowingLoading(false);
    }
  }, []);

  const refreshFollowers = useCallback(async () => {
    await getFollowers(0, 100);
  }, [getFollowers]);

  const refreshFollowing = useCallback(async () => {
    await getFollowing(0, 100);
  }, [getFollowing]);

  const isFollowing = useCallback(async (userId: string): Promise<boolean> => {
    try {
      const response = await apiService.isFollowing(userId);
      return response.is_following;
    } catch (error) {
      console.error('Check following status failed:', error);
      return false;
    }
  }, []);

  const getUserProfile = useCallback(async (userId: string): Promise<UserPublicExtended> => {
    try {
      return await apiService.getUserProfileExtended(userId);
    } catch (error) {
      console.error('Get user profile failed:', error);
      throw error;
    }
  }, []);


  const value: SocialContextType = {
    // Search state
    searchResults,
    searchLoading,
    searchError,
    
    // Followers/Following state
    followers,
    following,
    followersLoading,
    followingLoading,
    followersError,
    followingError,
    
    // Follow action state
    followActionLoading,
    
    // Methods
    searchUsers,
    clearSearchResults,
    followUser,
    unfollowUser,
    getFollowers,
    getFollowing,
    refreshFollowers,
    refreshFollowing,
    isFollowing,
    getUserProfile,
  };

  return (
    <SocialContext.Provider value={value}>
      {children}
    </SocialContext.Provider>
  );
};

export const useSocial = () => {
  const context = useContext(SocialContext);
  if (!context) {
    throw new Error('useSocial must be used within a SocialProvider');
  }
  return context;
};