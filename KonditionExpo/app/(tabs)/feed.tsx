import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { router } from 'expo-router';
import { useFeed, FeedType } from '../../contexts/FeedContext';
import { FeedToggle, PostList, CreatePostButton } from '../../components/feed';
import { WorkoutPostResponse } from '../../services/api';

export default function FeedScreen() {
  const {
    getCurrentFeed,
    currentFeedType,
    setCurrentFeedType,
    loadFeed,
    loadMorePosts,
    refreshFeed,
    isLoading,
    error,
    hasMore,
    personalFeed,
    publicFeed,
    combinedFeed,
    clearError,
  } = useFeed();

  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    // Load initial feed when component mounts
    loadFeed(currentFeedType, true);
  }, []);

  useEffect(() => {
    // Show error alert if there's an error
    if (error) {
      Alert.alert('Error', error, [
        { text: 'OK', onPress: clearError }
      ]);
    }
  }, [error, clearError]);

  const handleFeedTypeChange = async (feedType: FeedType) => {
    setCurrentFeedType(feedType);
    
    // Load feed if it's empty or switch to a different type
    const targetFeed = getFeedForType(feedType);
    if (targetFeed.length === 0) {
      await loadFeed(feedType, true);
    }
  };

  const getFeedForType = (feedType: FeedType): WorkoutPostResponse[] => {
    switch (feedType) {
      case 'personal':
        return personalFeed;
      case 'public':
        return publicFeed;
      case 'combined':
        return combinedFeed;
      default:
        return personalFeed;
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await refreshFeed();
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleLoadMore = async () => {
    await loadMorePosts();
  };

  const handleCreatePost = () => {
    router.push('/create-post' as any);
  };

  const handlePostPress = (post: WorkoutPostResponse) => {
    // Navigate to post detail or user profile
    console.log('Post pressed:', post.id);
    // TODO: Implement post detail navigation
  };

  const postCounts = {
    personal: personalFeed.length,
    public: publicFeed.length,
    combined: combinedFeed.length,
  };

  const currentFeed = getCurrentFeed();

  return (
    <View style={styles.container}>
      <FeedToggle
        currentFeedType={currentFeedType}
        onFeedTypeChange={handleFeedTypeChange}
        postCounts={postCounts}
      />
      
      <PostList
        posts={currentFeed}
        isLoading={isLoading}
        isRefreshing={isRefreshing}
        hasMore={hasMore}
        onRefresh={handleRefresh}
        onLoadMore={handleLoadMore}
        onPostPress={handlePostPress}
      />
      
      <CreatePostButton onPress={handleCreatePost} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
});