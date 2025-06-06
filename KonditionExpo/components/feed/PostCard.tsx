import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, ActivityIndicator, Platform } from 'react-native';
import { WorkoutPostResponse } from '../../services/api';
import { useFeed } from '../../contexts/FeedContext';
import { useAuth } from '../../contexts/AuthContext';
import { IconSymbol } from '../ui/IconSymbol';

interface PostCardProps {
  post: WorkoutPostResponse;
  onPress?: () => void;
}

export function PostCard({ post, onPress }: PostCardProps) {
  const { deletePost } = useFeed();
  const { user } = useAuth();
  const [isDeleting, setIsDeleting] = useState(false);
  
  const isOwnPost = user?.id === post.user_id;
  
  // Enhanced debug logging to help identify the issue
  console.log('PostCard Debug:', {
    currentUserId: user?.id,
    currentUserIdType: typeof user?.id,
    postUserId: post.user_id,
    postUserIdType: typeof post.user_id,
    isOwnPost,
    userFullName: user?.full_name,
    postUserName: post.user_full_name,
    postTitle: post.title,
    strictEquality: user?.id === post.user_id,
    looseEquality: user?.id == post.user_id
  });
  
  const formatDuration = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes}m`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  };

  const formatTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return date.toLocaleDateString();
  };

  const handleDelete = async () => {
    console.log('Delete button pressed for post:', post.id, 'by user:', user?.id);
    
    if (isDeleting) {
      console.log('Delete already in progress, ignoring click');
      return; // Prevent multiple delete attempts
    }
    
    console.log('Showing delete confirmation dialog');
    
    // Use web-compatible confirmation for web platform
    if (Platform.OS === 'web') {
      const confirmed = window.confirm('Are you sure you want to delete this post?');
      if (!confirmed) {
        console.log('User cancelled delete');
        return;
      }
    } else {
      // Use Alert.alert for native platforms
      return new Promise((resolve) => {
        Alert.alert(
          'Delete Post',
          'Are you sure you want to delete this post?',
          [
            {
              text: 'Cancel',
              style: 'cancel',
              onPress: () => {
                console.log('User cancelled delete');
                resolve(false);
              }
            },
            {
              text: 'Delete',
              style: 'destructive',
              onPress: () => {
                console.log('User confirmed delete via Alert');
                resolve(true);
              },
            },
          ]
        );
      }).then((confirmed) => {
        if (!confirmed) return;
        return performDelete();
      });
    }
    
    // For web, proceed directly after confirmation
    console.log('User confirmed delete, starting deletion process...');
    await performDelete();
  };

  const performDelete = async () => {
    try {
      setIsDeleting(true);
      console.log('Calling deletePost with ID:', post.id);
      await deletePost(post.id);
      console.log('Delete post successful');
      // Success feedback is handled by optimistic update in FeedContext
    } catch (error) {
      console.error('Delete post error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete post';
      console.log('Showing error alert:', errorMessage);
      
      if (Platform.OS === 'web') {
        window.alert(`Delete Failed: ${errorMessage}`);
      } else {
        Alert.alert(
          'Delete Failed',
          errorMessage,
          [{ text: 'OK', style: 'default' }]
        );
      }
    } finally {
      console.log('Delete process completed, resetting isDeleting state');
      setIsDeleting(false);
    }
  };

  return (
    <TouchableOpacity style={styles.container} onPress={onPress} activeOpacity={0.7}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.userInfo}>
          <View style={styles.avatar}>
            <IconSymbol name="person.fill" size={20} color="#666" />
          </View>
          <View style={styles.userDetails}>
            <Text style={styles.userName}>{post.user_full_name || 'Unknown User'}</Text>
            <View style={styles.metaInfo}>
              <Text style={styles.timestamp}>{formatTimeAgo(post.created_at)}</Text>
              <View style={styles.privacyIndicator}>
                <IconSymbol 
                  name={post.is_public ? "globe" : "lock.fill"} 
                  size={12} 
                  color={post.is_public ? "#4CAF50" : "#FF9800"} 
                />
                <Text style={[styles.privacyText, { color: post.is_public ? "#4CAF50" : "#FF9800" }]}>
                  {post.is_public ? "Public" : "Private"}
                </Text>
              </View>
            </View>
          </View>
        </View>
        {/* Only show delete button for user's own posts */}
        {isOwnPost && (
          <TouchableOpacity
            onPress={handleDelete}
            style={[styles.deleteButton, isDeleting && styles.deleteButtonDisabled]}
            disabled={isDeleting}
            activeOpacity={0.8}
            hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
          >
            {isDeleting ? (
              <ActivityIndicator size="small" color="#FFFFFF" />
            ) : (
              <IconSymbol name="trash" size={18} color="#FFFFFF" />
            )}
          </TouchableOpacity>
        )}
      </View>

      {/* Content */}
      <View style={styles.content}>
        <Text style={styles.title}>{post.title}</Text>
        {post.description && (
          <Text style={styles.description}>{post.description}</Text>
        )}
        
        {/* Workout Details */}
        <View style={styles.workoutDetails}>
          <View style={styles.workoutType}>
            <IconSymbol name="figure.run" size={16} color="#007AFF" />
            <Text style={styles.workoutTypeText}>{post.workout_type}</Text>
          </View>
          
          <View style={styles.stats}>
            <View style={styles.stat}>
              <IconSymbol name="clock" size={14} color="#666" />
              <Text style={styles.statText}>{formatDuration(post.duration_minutes)}</Text>
            </View>
            
            {post.calories_burned && (
              <View style={styles.stat}>
                <IconSymbol name="flame" size={14} color="#FF6B35" />
                <Text style={styles.statText}>{post.calories_burned} cal</Text>
              </View>
            )}
          </View>
        </View>
      </View>

      {/* Footer - Placeholder for future interactions */}
      <View style={styles.footer}>
        <TouchableOpacity style={styles.actionButton}>
          <IconSymbol name="heart" size={16} color="#666" />
          <Text style={styles.actionText}>Like</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton}>
          <IconSymbol name="message" size={16} color="#666" />
          <Text style={styles.actionText}>Comment</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton}>
          <IconSymbol name="square.and.arrow.up" size={16} color="#666" />
          <Text style={styles.actionText}>Share</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  userDetails: {
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  metaInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  timestamp: {
    fontSize: 12,
    color: '#666',
    marginRight: 8,
  },
  privacyIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  privacyText: {
    fontSize: 11,
    fontWeight: '500',
    marginLeft: 4,
  },
  deleteButton: {
    padding: 10,
    borderRadius: 8,
    backgroundColor: '#FF3B30',
    borderWidth: 2,
    borderColor: '#FF1F1F',
    minWidth: 40,
    minHeight: 40,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#FF3B30',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  deleteButtonDisabled: {
    opacity: 0.6,
    backgroundColor: '#FF8A80',
    borderColor: '#FF8A80',
  },
  content: {
    marginBottom: 12,
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
    marginBottom: 6,
  },
  description: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  workoutDetails: {
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 12,
  },
  workoutType: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  workoutTypeText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#007AFF',
    marginLeft: 6,
  },
  stats: {
    flexDirection: 'row',
    gap: 16,
  },
  stat: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 4,
    fontWeight: '500',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  actionText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 4,
    fontWeight: '500',
  },
});