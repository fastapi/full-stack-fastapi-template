import React from 'react';
import { FlatList, View, Text, StyleSheet, RefreshControl, ActivityIndicator } from 'react-native';
import { WorkoutPostResponse } from '../../services/api';
import { PostCard } from './PostCard';

interface PostListProps {
  posts: WorkoutPostResponse[];
  isLoading: boolean;
  isRefreshing: boolean;
  hasMore: boolean;
  onRefresh: () => void;
  onLoadMore: () => void;
  onPostPress?: (post: WorkoutPostResponse) => void;
}

export function PostList({
  posts,
  isLoading,
  isRefreshing,
  hasMore,
  onRefresh,
  onLoadMore,
  onPostPress,
}: PostListProps) {
  const renderPost = ({ item }: { item: WorkoutPostResponse }) => (
    <PostCard
      post={item}
      onPress={() => onPostPress?.(item)}
    />
  );

  const renderFooter = () => {
    if (!isLoading || isRefreshing) return null;
    
    return (
      <View style={styles.footer}>
        <ActivityIndicator size="small" color="#007AFF" />
        <Text style={styles.loadingText}>Loading more posts...</Text>
      </View>
    );
  };

  const renderEmpty = () => {
    if (isLoading && !isRefreshing) {
      return (
        <View style={styles.emptyContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.emptyText}>Loading posts...</Text>
        </View>
      );
    }

    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyTitle}>No posts yet</Text>
        <Text style={styles.emptyText}>
          Be the first to share your workout or follow some users to see their posts!
        </Text>
      </View>
    );
  };

  const handleEndReached = () => {
    if (hasMore && !isLoading) {
      onLoadMore();
    }
  };

  return (
    <FlatList
      data={posts}
      renderItem={renderPost}
      keyExtractor={(item) => item.id}
      refreshControl={
        <RefreshControl
          refreshing={isRefreshing}
          onRefresh={onRefresh}
          colors={['#007AFF']}
          tintColor="#007AFF"
        />
      }
      onEndReached={handleEndReached}
      onEndReachedThreshold={0.1}
      ListFooterComponent={renderFooter}
      ListEmptyComponent={renderEmpty}
      showsVerticalScrollIndicator={false}
      contentContainerStyle={posts.length === 0 ? styles.emptyList : undefined}
    />
  );
}

const styles = StyleSheet.create({
  footer: {
    paddingVertical: 20,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 8,
    fontSize: 14,
    color: '#666',
  },
  emptyList: {
    flex: 1,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
    paddingVertical: 64,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
});