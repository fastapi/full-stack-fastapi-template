import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Alert, TouchableOpacity, KeyboardAvoidingView, Platform } from 'react-native';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { router } from 'expo-router';
import { useAuth } from '@/contexts/AuthContext';
import { useThemeColor } from '../hooks/useThemeColor';

export default function SignUpScreen() {
  const { signup, isLoading, isAuthenticated } = useAuth();
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState<{
    email?: string;
    fullName?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  const backgroundColor = useThemeColor({}, 'background');
  const textColor = useThemeColor({}, 'text');
  const tintColor = useThemeColor({}, 'tint');

  // Note: We don't redirect authenticated users here anymore since we want them
  // to complete the profile setup flow after signup

  const validateForm = () => {
    const newErrors: typeof errors = {};

    // Full name validation
    if (!fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    } else if (fullName.trim().length < 2) {
      newErrors.fullName = 'Full name must be at least 2 characters';
    }

    // Email validation
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Please enter a valid email';
    }

    // Password validation
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      newErrors.password = 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
    }

    // Confirm password validation
    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = "Passwords don't match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleCreateAccount = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      console.log('Starting signup process...');
      await signup({
        email: email.trim(),
        password,
        full_name: fullName.trim(),
      });
      
      console.log('Signup successful, user is now logged in. Navigating to profile completion...');
      // User is now logged in automatically, redirect to profile completion
      router.replace('/signup2');
      console.log('Navigation to profile completion initiated');
    } catch (error) {
      console.error('Signup error:', error);
      Alert.alert(
        'Signup Failed',
        error instanceof Error ? error.message : 'An unexpected error occurred. Please try again.',
        [{ text: 'OK' }]
      );
    }
  };

  const handleSignIn = () => {
    router.push('/login');
  };

  return (
    <KeyboardAvoidingView
      style={[styles.container, { backgroundColor }]}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.formContainer}>
          <Text style={[styles.title, { color: textColor }]}>Create Your Account</Text>
          <Text style={[styles.subtitle, { color: textColor }]}>Join Kondition and start your fitness journey</Text>

          <Input
            label="Full Name"
            value={fullName}
            onChangeText={setFullName}
            placeholder="Enter your full name"
            autoCapitalize="words"
            error={errors.fullName}
          />

          <Input
            label="Email"
            value={email}
            onChangeText={setEmail}
            placeholder="Enter your email"
            keyboardType="email-address"
            autoCapitalize="none"
            error={errors.email}
          />

          <Input
            label="Password"
            value={password}
            onChangeText={setPassword}
            placeholder="Enter your password"
            secureTextEntry={!showPassword}
            error={errors.password}
            rightIcon={
              <TouchableOpacity
                onPress={() => setShowPassword(!showPassword)}
                accessibilityLabel={showPassword ? 'Hide password' : 'Show password'}
                accessibilityRole="button"
                accessible={true}
              >
                <Text style={{ color: tintColor }}>{showPassword ? 'Hide' : 'Show'}</Text>
              </TouchableOpacity>
            }
          />

          <Input
            label="Confirm Password"
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            placeholder="Confirm your password"
            secureTextEntry={!showConfirmPassword}
            error={errors.confirmPassword}
            rightIcon={
              <TouchableOpacity
                onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                accessibilityLabel={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
                accessibilityRole="button"
                accessible={true}
              >
                <Text style={{ color: tintColor }}>{showConfirmPassword ? 'Hide' : 'Show'}</Text>
              </TouchableOpacity>
            }
          />

          <Button
            title="Create Account"
            onPress={handleCreateAccount}
            loading={isLoading}
            loadingText="Creating Account..."
            fullWidth={true}
            style={styles.signupButton}
          />

          <View style={styles.signinContainer}>
            <Text style={{ color: textColor }}>Already have an account? </Text>
            <TouchableOpacity
              onPress={handleSignIn}
              accessibilityLabel="Sign In"
              accessibilityRole="button"
              accessible={true}
            >
              <Text style={{ color: tintColor, fontWeight: '600' }}>Sign In</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 24,
    justifyContent: 'center',
  },
  formContainer: {
    width: '100%',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 32,
    textAlign: 'center',
    opacity: 0.8,
  },
  signupButton: {
    marginTop: 8,
    marginBottom: 24,
  },
  signinContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
});
