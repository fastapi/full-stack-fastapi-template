import React from 'react';
import { TouchableOpacity, ActivityIndicator, Text, StyleSheet, View } from 'react-native';
import { useThemeColor } from '../../hooks/useThemeColor';

interface ButtonProps {
  onPress?: () => void;
  title: string;
  loading?: boolean;
  loadingText?: string;
  disabled?: boolean;
  variant?: 'solid' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  colorScheme?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  style?: any;
  textStyle?: any;
}

export function Button({ 
  onPress, 
  title, 
  loading = false, 
  loadingText, 
  disabled = false, 
  variant = 'solid', 
  size = 'md', 
  colorScheme = 'primary',
  leftIcon,
  rightIcon,
  fullWidth = false,
  style,
  textStyle
}: ButtonProps) {
  const tintColor = useThemeColor({}, 'tint');
  const textColor = useThemeColor({}, 'text');
  const backgroundColor = tintColor;
  const disabledBg = '#A0AEC0';
  
  // Apply variant styles
  let variantStyle = {};
  let variantTextStyle = {};
  
  if (variant === 'outline') {
    variantStyle = {
      backgroundColor: 'transparent',
      borderWidth: 1,
      borderColor: backgroundColor,
    };
    variantTextStyle = {
      color: backgroundColor,
    };
  } else if (variant === 'ghost') {
    variantStyle = {
      backgroundColor: 'transparent',
    };
    variantTextStyle = {
      color: backgroundColor,
    };
  }
  
  // Apply size styles
  let sizeStyle = styles.buttonMd;
  let sizeTextStyle = styles.textMd;
  
  if (size === 'sm') {
    sizeStyle = styles.buttonSm;
    sizeTextStyle = styles.textSm;
  } else if (size === 'lg') {
    sizeStyle = styles.buttonLg;
    sizeTextStyle = styles.textLg;
  }
  
  // Apply width style
  const widthStyle = fullWidth ? { width: '100%' } : {};
  
  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      style={[
        styles.button,
        sizeStyle,
        { backgroundColor: disabled ? disabledBg : backgroundColor },
        variantStyle,
        widthStyle,
        style,
      ]}
      activeOpacity={0.7}
    >
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator color={variant === 'solid' ? 'white' : textColor} />
          {loadingText && <Text style={[styles.text, sizeTextStyle, variantTextStyle, textStyle, { marginLeft: 8 }]}>{loadingText}</Text>}
        </View>
      ) : (
        <View style={styles.contentContainer}>
          {leftIcon && <View style={styles.iconLeft}>{leftIcon}</View>}
          <Text style={[styles.text, sizeTextStyle, variantTextStyle, textStyle]}>{title}</Text>
          {rightIcon && <View style={styles.iconRight}>{rightIcon}</View>}
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 6,
  },
  buttonSm: {
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  buttonMd: {
    paddingVertical: 10,
    paddingHorizontal: 20,
  },
  buttonLg: {
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  text: {
    fontWeight: '600',
    color: 'white',
  },
  textSm: {
    fontSize: 14,
  },
  textMd: {
    fontSize: 16,
  },
  textLg: {
    fontSize: 18,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  contentContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconLeft: {
    marginRight: 8,
  },
  iconRight: {
    marginLeft: 8,
  }
}); 