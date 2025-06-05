import React from 'react';
import {
  FlatList,
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
  ListRenderItem,
} from 'react-native';
import { UserSearchResult, UserProfile } from '../../services/api';
import { UserCard } from './UserCard';

interface UserListProps {
  users: (UserSearchResult | UserProfile)[];
  loading?: boolean;
  refreshing?: boolean;
  onRefresh?: () => void;
  onLoadMore?: () => void;
  onUserPress?: (user: UserSearchResult | UserProfile) => void;
  showFollowButton?: boolean;
  emptyTitle?: string;
  emptyMessage?: string;
  size?: 'compact' | 'normal';
  hasMore?: boolean;
  context?: 'following' | 'followers' | 'search';
}

export const UserList: React.FC<UserListProps> = ({
  users,
  loading = false,
  refreshing = false,
  onRefresh,
  onLoadMore,
  onUserPress,
  showFollowButton = true,
  emptyTitle = "No Users Found",
  emptyMessage = "Try searching for users or check back later.",
  size = 'normal',
  hasMore = false,
  context = 'search',
}) => {
  const renderUser: ListRenderItem<UserSearchResult | UserProfile> = ({ item }) => (
    <UserCard
      user={item}
      onPress={onUserPress ? () => onUserPress(item) : undefined}
      showFollowButton={showFollowButton}
      size={size}
      context={context}
    />
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyTitle}>{emptyTitle}</Text>
      <Text style={styles.emptyMessage}>{emptyMessage}</Text>
    </View>
  );

  const renderFooter = () => {
    if (!loading || users.length === 0) return null;
    
    return (
      <View style={styles.footer}>
        <ActivityIndicator size="small" color="#70A1FF" />
        <Text style={styles.footerText}>Loading more users...</Text>
      </View>
    );
  };

  const handleEndReached = () => {
    if (!loading && hasMore && onLoadMore) {
      onLoadMore();
    }
  };

  if (loading && users.length === 0) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#70A1FF" />
        <Text style={styles.loadingText}>Loading users...</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={users}
      renderItem={renderUser}
      keyExtractor={(item) => item.id}
      contentContainerStyle={[
        styles.container,
        users.length === 0 && styles.emptyContainer,
      ]}
      showsVerticalScrollIndicator={false}
      refreshControl={
        onRefresh ? (
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={['#70A1FF']}
            tintColor="#70A1FF"
          />
        ) : undefined
      }
      ListEmptyComponent={renderEmptyState}
      ListFooterComponent={renderFooter}
      onEndReached={handleEndReached}
      onEndReachedThreshold={0.1}
      removeClippedSubviews={true}
      maxToRenderPerBatch={10}
      windowSize={10}
      initialNumToRender={10}
    />
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
    paddingHorizontal: 32,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyMessage: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 16,
  },
  footerText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666',
  },
});