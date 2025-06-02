import React, { useState } from 'react';
import { View, TextInput, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useThemeColor } from '../../hooks/useThemeColor';

interface InputProps {
  placeholder?: string;
  value: string;
  onChangeText: (text: string) => void;
  label?: string;
  error?: string;
  isRequired?: boolean;
  autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';
  keyboardType?: 'default' | 'email-address' | 'numeric' | 'phone-pad' | 'number-pad';
  secureTextEntry?: boolean;
  multiline?: boolean;
  numberOfLines?: number;
  style?: any;
  inputStyle?: any;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  onRightIconPress?: () => void;
}

export function Input({
  placeholder,
  value,
  onChangeText,
  label,
  error,
  isRequired = false,
  autoCapitalize = 'none',
  keyboardType = 'default',
  secureTextEntry = false,
  multiline = false,
  numberOfLines = 1,
  style,
  inputStyle,
  leftIcon,
  rightIcon,
  onRightIconPress,
}: InputProps) {
  const [isFocused, setIsFocused] = useState(false);
  
  const textColor = useThemeColor({}, 'text');
  const tintColor = useThemeColor({}, 'tint');
  const backgroundColor = useThemeColor({}, 'background');
  
  const borderColor = error ? '#E53E3E' : isFocused ? tintColor : '#E2E8F0';
  
  return (
    <View style={[styles.container, style]}>
      {label && (
        <View style={styles.labelContainer}>
          <Text style={[styles.label, { color: textColor }]}>
            {label}
            {isRequired && <Text style={{ color: '#E53E3E' }}> *</Text>}
          </Text>
        </View>
      )}
      
      <View 
        style={[
          styles.inputContainer, 
          { 
            borderColor,
            backgroundColor,
          },
          multiline && { height: numberOfLines * 24 + 16 },
        ]}
      >
        {leftIcon && <View style={styles.leftIcon}>{leftIcon}</View>}
        
        <TextInput
          placeholder={placeholder}
          value={value}
          onChangeText={onChangeText}
          style={[
            styles.input,
            { color: textColor },
            leftIcon && { paddingLeft: 0 },
            rightIcon && { paddingRight: 0 },
            multiline && { textAlignVertical: 'top' },
            inputStyle,
          ]}
          autoCapitalize={autoCapitalize}
          keyboardType={keyboardType}
          secureTextEntry={secureTextEntry}
          multiline={multiline}
          numberOfLines={multiline ? numberOfLines : undefined}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholderTextColor="#A0AEC0"
          accessibilityLabel={label || placeholder}
          accessibilityHint={error ? `Error: ${error}` : undefined}
          accessibilityRole="text"
          accessible={true}
        />
        
        {rightIcon && (
          onRightIconPress ? (
            <TouchableOpacity
              style={styles.rightIcon}
              onPress={onRightIconPress}
              accessibilityRole="button"
              accessible={true}
            >
              {rightIcon}
            </TouchableOpacity>
          ) : (
            <View style={styles.rightIcon}>
              {rightIcon}
            </View>
          )
        )}
      </View>
      
      {error && (
        <Text style={styles.error}>{error}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  labelContainer: {
    marginBottom: 4,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: 6,
    overflow: 'hidden',
  },
  input: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 12,
    fontSize: 16,
  },
  leftIcon: {
    paddingLeft: 12,
  },
  rightIcon: {
    paddingRight: 12,
  },
  error: {
    fontSize: 12,
    color: '#E53E3E',
    marginTop: 4,
  },
}); 