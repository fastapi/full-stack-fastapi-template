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
  const { isAuthenticated, isLoading, isInSignupFlow } = useAuth();
  const segments = useSegments();
  const backgroundColor = useThemeColor({}, 'background');
  const textColor = useThemeColor({}, 'text');

  useEffect(() => {
    if (!isLoading) {
      const currentRoute = segments[0];
      const inAuthGroup = currentRoute === '(tabs)' || currentRoute === 'workout' || currentRoute === 'notification' || currentRoute === 'profile' || currentRoute === 'home';
      const inPublicGroup = currentRoute === 'login' || currentRoute === 'signup';
      const isSignup2Route = currentRoute === 'signup2';
      
      console.log('ProtectedRoute: Current route:', currentRoute);
      console.log('ProtectedRoute: Segments:', segments);
      console.log('ProtectedRoute: isAuthenticated:', isAuthenticated);
      console.log('ProtectedRoute: isLoading:', isLoading);
      console.log('ProtectedRoute: isInSignupFlow:', isInSignupFlow);
      console.log('ProtectedRoute: inAuthGroup:', inAuthGroup);
      console.log('ProtectedRoute: inPublicGroup:', inPublicGroup);
      console.log('ProtectedRoute: isSignup2Route:', isSignup2Route);
      
      // Allow signup2 route for authenticated users during profile completion
      if (isSignup2Route) {
        console.log('ProtectedRoute: Allowing access to signup2 route');
        return;
      }
      
      if (!isAuthenticated && inAuthGroup) {
        // User is not authenticated but trying to access protected route
        console.log('ProtectedRoute: Redirecting to /login (not authenticated, trying to access protected route)');
        router.replace('/login');
      } else if (isAuthenticated && inPublicGroup && !isInSignupFlow) {
        // User is authenticated but on login/signup screens - redirect to main app
        // But don't redirect if they're in the signup flow (going to signup2)
        console.log('ProtectedRoute: Redirecting to /(tabs) (authenticated user on public route, not in signup flow)');
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