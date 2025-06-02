import React, { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { router, useSegments } from 'expo-router';
import { useAuth } from '@/contexts/AuthContext';
import { useThemeColor } from '@/hooks/useThemeColor';
import { ThemedText } from './ThemedText';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const segments = useSegments();
  const backgroundColor = useThemeColor({}, 'background');
  const textColor = useThemeColor({}, 'text');

  useEffect(() => {
    if (!isLoading) {
      const currentRoute = segments[0];
      const inAuthGroup = currentRoute === '(tabs)' || currentRoute === 'workout' || currentRoute === 'notification' || currentRoute === 'profile' || currentRoute === 'home';
      const inPublicGroup = currentRoute === 'login' || currentRoute === 'signup';
      
      if (!isAuthenticated && inAuthGroup) {
        // User is not authenticated but trying to access protected route
        router.replace('/login');
      } else if (isAuthenticated && inPublicGroup) {
        // User is authenticated but on auth screens
        router.replace('/(tabs)');
      }
      // For index route, let the index component handle the redirect
    }
  }, [isAuthenticated, isLoading, segments]);

  // Show loading screen while checking authentication
  if (isLoading) {
    return (
      <View style={[styles.loadingContainer, { backgroundColor }]}>
        <ActivityIndicator size="large" color={textColor} />
        <ThemedText style={styles.loadingText}>Loading...</ThemedText>
      </View>
    );
  }

  return <>{children}</>;
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