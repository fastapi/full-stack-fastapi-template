import React from 'react';
import { TouchableOpacity, Text, StyleSheet, View } from 'react-native';
import { useThemeColor } from '../../hooks/useThemeColor';

interface CheckboxProps {
  isChecked: boolean;
  onChange: (isChecked: boolean) => void;
  label?: string;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  style?: any;
}

export function Checkbox({
  isChecked,
  onChange,
  label,
  disabled = false,
  size = 'md',
  style,
}: CheckboxProps) {
  const tintColor = useThemeColor({}, 'tint');
  const textColor = useThemeColor({}, 'text');
  const iconColor = useThemeColor({}, 'icon');
  
  // Determine checkbox size
  let checkboxSize = 20;
  if (size === 'sm') checkboxSize = 16;
  if (size === 'lg') checkboxSize = 24;
  
  // Calculate internal checkmark size
  const checkmarkSize = checkboxSize - 8;
  
  return (
    <TouchableOpacity
      style={[
        styles.container,
        style,
      ]}
      onPress={() => {
        if (!disabled) {
          onChange(!isChecked);
        }
      }}
      activeOpacity={0.7}
      disabled={disabled}
      accessibilityLabel={label || 'Checkbox'}
      accessibilityRole="checkbox"
      accessibilityState={{ checked: isChecked, disabled }}
      accessible={true}
    >
      <View
        style={[
          styles.checkbox,
          {
            width: checkboxSize,
            height: checkboxSize,
            borderColor: disabled ? iconColor : tintColor,
            backgroundColor: isChecked ? (disabled ? iconColor : tintColor) : 'transparent',
          },
        ]}
      >
        {isChecked && (
          <View
            style={[
              styles.checkmark,
              {
                width: checkmarkSize,
                height: checkmarkSize,
              },
            ]}
          />
        )}
      </View>
      
      {label && (
        <Text
          style={[
            styles.label,
            {
              color: disabled ? iconColor : textColor,
              fontSize: size === 'sm' ? 14 : size === 'lg' ? 18 : 16,
            },
          ]}
        >
          {label}
        </Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 4,
  },
  checkbox: {
    borderWidth: 2,
    borderRadius: 4,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkmark: {
    backgroundColor: 'white',
    borderRadius: 2,
  },
  label: {
    marginLeft: 8,
  },
}); 