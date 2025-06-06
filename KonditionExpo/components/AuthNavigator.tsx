import React from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { Stack, router } from 'expo-router';
import { useAuth } from '@/contexts/AuthContext';
import { useThemeColor } from '@/hooks/useThemeColor';
import { ThemedText } from './ThemedText';

export function AuthNavigator() {
  const { isAuthenticated, isLoading } = useAuth();
  const backgroundColor = useThemeColor({}, 'background');
  const textColor = useThemeColor({}, 'text');

  // Show loading screen while checking authentication
  if (isLoading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor }]}>
        <ActivityIndicator size="large" color={textColor} />
        <ThemedText style={styles.loadingText}>Loading...</ThemedText>
      </View>
    );
  }

  // Redirect based on authentication state
  React.useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        // User is authenticated, redirect to main app
        router.replace('/(tabs)');
      } else {
        // User is not authenticated, redirect to login
        router.replace('/login');
      }
    }
  }, [isAuthenticated, isLoading]);

  // Render the stack navigator
  return (
    <Stack>
      {isAuthenticated ? (
        // Authenticated routes
        <>
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
          <Stack.Screen name="workout" options={{ headerShown: false }} />
          <Stack.Screen name="notification" options={{ headerShown: false }} />
          <Stack.Screen name="profile" options={{ headerShown: false }} />
          <Stack.Screen name="home" options={{ headerShown: false }} />
        </>
      ) : (
        // Unauthenticated routes
        <>
          <Stack.Screen name="login" options={{ headerShown: false }} />
          <Stack.Screen name="signup" options={{ headerShown: false }} />
          <Stack.Screen name="signup2" options={{ headerShown: false }} />
        </>
      )}
      <Stack.Screen name="+not-found" />
    </Stack>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
  },
});