import React, { useState, useEffect } from 'react';
import { View, StyleSheet, TouchableOpacity, Text, Image, KeyboardAvoidingView, Platform, ScrollView, Alert } from 'react-native';
import { useThemeColor } from '../hooks/useThemeColor';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Checkbox } from '../components/ui/Checkbox';
import { router } from 'expo-router';
import { useAuth } from '@/contexts/AuthContext';

export default function LoginScreen() {
  const { login, isLoading, isAuthenticated } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  
  const backgroundColor = useThemeColor({}, 'background');
  const textColor = useThemeColor({}, 'text');
  const tintColor = useThemeColor({}, 'tint');

  // Redirect if already authenticated -- Might want to remove since i think we don't have logout
  /*useEffect(() => {
    if (isAuthenticated) {
      router.replace('/(tabs)');
    }
  }, [isAuthenticated]);*/
  
  const handleLogin = async () => {
    setErrors({});
    
    const newErrors: { email?: string; password?: string } = {};
  
    if (!email) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(email)) newErrors.email = 'Please enter a valid email';
  
    if (!password) newErrors.password = 'Password is required';
    else if (password.length < 6) newErrors.password = 'Password must be at least 6 characters';
  
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
  
    try {
      await login(email, password);
      // Navigation will happen automatically via useEffect when isAuthenticated becomes true
    } catch (error) {
      console.error('Login error:', error);
      Alert.alert(
        'Login Failed',
        error instanceof Error ? error.message : 'An unexpected error occurred. Please try again.',
        [{ text: 'OK' }]
      );
    }
  };
  
  const handleForgotPassword = () => {
    router.push('/(tabs)');
  };
  
  const handleSignUp = () => {
    router.push('/signup'); // created a new screen for signup (signup.tsx)
  };
  
  
  return (
    <KeyboardAvoidingView
      style={[styles.container, { backgroundColor }]}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.logoContainer}>
          <Image 
            source={require('../assets/images/icon.png')} 
            style={styles.logo} 
            resizeMode="contain"
          />
          <Text style={[styles.appName, { color: textColor }]}>Kondition</Text>
        </View>
        
        <View style={styles.formContainer}>
          <Text style={[styles.heading, { color: textColor }]}>Welcome Back</Text>
          <Text style={[styles.subheading, { color: textColor }]}>Sign in to your account</Text>
          
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
          
          <View style={styles.optionsRow}>
            <Checkbox
              isChecked={rememberMe}
              onChange={setRememberMe}
              label="Remember me"
            />
            
            <TouchableOpacity
              onPress={handleForgotPassword}
              accessibilityLabel="Forgot Password"
              accessibilityRole="button"
              accessible={true}
            >
              <Text style={[styles.forgotPassword, { color: tintColor }]}>Forgot Password?</Text>
            </TouchableOpacity>
          </View>
          
          <Button
            title="Sign In"
            onPress={handleLogin}
            loading={isLoading}
            loadingText="Signing In..."
            fullWidth={true}
            style={styles.loginButton}
          />
          
          <View style={styles.signupContainer}>
            <Text style={{ color: textColor }}>Don't have an account? </Text>
            <TouchableOpacity
              onPress={handleSignUp}
              accessibilityLabel="Sign Up"
              accessibilityRole="button"
              accessible={true}
            >
              <Text style={{ color: tintColor, fontWeight: '600' }}>Sign Up</Text>
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
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logo: {
    width: 80,
    height: 80,
    marginBottom: 16,
  },
  appName: {
    fontSize: 28,
    fontWeight: 'bold',
  },
  formContainer: {
    width: '100%',
  },
  heading: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subheading: {
    fontSize: 16,
    marginBottom: 24,
    opacity: 0.8,
  },
  optionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  forgotPassword: {
    fontSize: 14,
  },
  loginButton: {
    marginBottom: 24,
  },
  signupContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
}); 