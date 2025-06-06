import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { UserSearchResult, UserProfile } from '../../services/api';
import { FollowButton } from './FollowButton';
import { useSocial } from '../../contexts/SocialContext';

interface UserCardProps {
  user: UserSearchResult | UserProfile;
  onPress?: () => void;
  showFollowButton?: boolean;
  size?: 'compact' | 'normal';
  context?: 'following' | 'followers' | 'search';
}

export const UserCard: React.FC<UserCardProps> = ({
  user,
  onPress,
  showFollowButton = true,
  size = 'normal',
  context = 'search',
}) => {
  const { followUser, unfollowUser, followActionLoading } = useSocial();
  
  // Determine follow status based on context
  const isFollowing = (() => {
    if (context === 'following') {
      // Users in Following tab should always show as following (for Unfollow button)
      console.log(`[UserCard] Following context - User: ${user.full_name || user.email}, forcing isFollowing=true`);
      return true;
    } else if (context === 'followers') {
      // Users in Followers tab show follow status based on whether we follow them back
      const followStatus = 'is_following' in user ? (user.is_following ?? false) : false;
      console.log(`[UserCard] Followers context - User: ${user.full_name || user.email}, is_following: ${followStatus}`);
      return followStatus;
    } else {
      // Search results use the is_following property
      const followStatus = 'is_following' in user ? (user.is_following ?? false) : false;
      console.log(`[UserCard] Search context - User: ${user.full_name || user.email}, is_following: ${followStatus}`);
      return followStatus;
    }
  })();
  const followerCount = 'follower_count' in user ? (user.follower_count ?? 0) : 0;
  const followingCount = 'following_count' in user ? (user.following_count ?? 0) : 0;
  const isLoading = followActionLoading[user.id] || false;

  const handleFollowPress = async () => {
    try {
      if (isFollowing) {
        await unfollowUser(user.id);
      } else {
        await followUser(user.id);
      }
    } catch (error) {
      Alert.alert(
        'Error',
        error instanceof Error ? error.message : 'Failed to update follow status',
        [{ text: 'OK' }]
      );
    }
  };

  const formatCount = (count: number): string => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M`;
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K`;
    }
    return count.toString();
  };

  const cardStyle = [
    styles.card,
    size === 'compact' && styles.compactCard,
  ];

  const avatarStyle = [
    styles.avatar,
    size === 'compact' && styles.compactAvatar,
  ];

  return (
    <TouchableOpacity
      style={cardStyle}
      onPress={onPress}
      activeOpacity={onPress ? 0.7 : 1}
      disabled={!onPress}
    >
      <View style={styles.leftSection}>
        <View style={avatarStyle}>
          <Ionicons 
            name="person" 
            size={size === 'compact' ? 20 : 24} 
            color="#70A1FF" 
          />
        </View>
        
        <View style={styles.userInfo}>
          <Text style={[styles.name, size === 'compact' && styles.compactName]} numberOfLines={1}>
            {user.full_name || 'Unknown User'}
          </Text>
          <Text style={[styles.email, size === 'compact' && styles.compactEmail]} numberOfLines={1}>
            {user.email}
          </Text>
          
          {size === 'normal' && (followerCount > 0 || followingCount > 0) && (
            <View style={styles.statsContainer}>
              <View style={styles.stat}>
                <Text style={styles.statNumber}>{formatCount(followerCount)}</Text>
                <Text style={styles.statLabel}>followers</Text>
              </View>
              <View style={styles.stat}>
                <Text style={styles.statNumber}>{formatCount(followingCount)}</Text>
                <Text style={styles.statLabel}>following</Text>
              </View>
            </View>
          )}
        </View>
      </View>
      
      {showFollowButton && (
        <FollowButton
          isFollowing={isFollowing}
          loading={isLoading}
          onPress={handleFollowPress}
          size={size === 'compact' ? 'small' : 'medium'}
        />
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#FFFFFF',
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 4,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
    borderWidth: 1,
    borderColor: '#F0F0F0',
  },
  compactCard: {
    padding: 12,
    marginVertical: 2,
  },
  leftSection: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: 12,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F8F9FA',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
    borderWidth: 1,
    borderColor: '#E9ECEF',
  },
  compactAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    marginRight: 10,
  },
  userInfo: {
    flex: 1,
  },
  name: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  compactName: {
    fontSize: 14,
    marginBottom: 1,
  },
  email: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  compactEmail: {
    fontSize: 12,
  },
  statsContainer: {
    flexDirection: 'row',
    marginTop: 4,
  },
  stat: {
    marginRight: 16,
  },
  statNumber: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
});