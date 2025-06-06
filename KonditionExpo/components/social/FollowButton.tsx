import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
} from 'react-native';

interface FollowButtonProps {
  isFollowing: boolean;
  loading?: boolean;
  onPress: () => void;
  disabled?: boolean;
  size?: 'small' | 'medium' | 'large';
  style?: ViewStyle;
}

export const FollowButton: React.FC<FollowButtonProps> = ({
  isFollowing,
  loading = false,
  onPress,
  disabled = false,
  size = 'medium',
  style,
}) => {
  const buttonStyle = [
    styles.button,
    styles[size],
    isFollowing ? styles.followingButton : styles.followButton,
    disabled && styles.disabledButton,
    style,
  ];

  const textStyle = [
    styles.text,
    styles[`${size}Text`],
    isFollowing ? styles.followingText : styles.followText,
    disabled && styles.disabledText,
  ];

  return (
    <TouchableOpacity
      style={buttonStyle}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.7}
    >
      {loading ? (
        <ActivityIndicator 
          size="small" 
          color={isFollowing ? "#70A1FF" : "#FFFFFF"} 
        />
      ) : (
        <Text style={textStyle}>
          {isFollowing ? 'Unfollow' : 'Follow'}
        </Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
  },
  
  // Sizes
  small: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    minWidth: 70,
  },
  medium: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    minWidth: 80,
  },
  large: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    minWidth: 100,
  },
  
  // Follow state styles
  followButton: {
    backgroundColor: '#70A1FF',
    borderColor: '#70A1FF',
  },
  followingButton: {
    backgroundColor: '#FFFFFF',
    borderColor: '#70A1FF',
  },
  
  // Disabled state
  disabledButton: {
    backgroundColor: '#F8F9FA',
    borderColor: '#E9ECEF',
  },
  
  // Text styles
  text: {
    fontWeight: '600',
  },
  smallText: {
    fontSize: 12,
  },
  mediumText: {
    fontSize: 14,
  },
  largeText: {
    fontSize: 16,
  },
  
  // Text colors
  followText: {
    color: '#FFFFFF',
  },
  followingText: {
    color: '#70A1FF',
  },
  disabledText: {
    color: '#999',
  },
});