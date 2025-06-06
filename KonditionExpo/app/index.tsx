import React, { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { router, useSegments } from 'expo-router';
import { useAuth } from '@/contexts/AuthContext';
import { useThemeColor } from '@/hooks/useThemeColor';
import { ThemedText } from '@/components/ThemedText';

export default function IndexScreen() {
  const { isAuthenticated, isLoading, isInSignupFlow } = useAuth();
  const segments = useSegments();
  const backgroundColor = useThemeColor({}, 'background');
  const textColor = useThemeColor({}, 'text');

  useEffect(() => {
    if (!isLoading) {
      // Don't redirect if we're already on a specific route (like signup2)
      const currentRoute = segments[0];
      if (currentRoute) {
        console.log('IndexScreen: Already on route:', currentRoute, '- not redirecting');
        return;
      }
      
      // Don't redirect if user is in signup flow - let them complete it
      if (isInSignupFlow) {
        console.log('IndexScreen: User in signup flow - not redirecting');
        return;
      }
      
      if (isAuthenticated) {
        router.replace('/(tabs)');
      } else {
        router.replace('/login');
      }
    }
  }, [isAuthenticated, isLoading, isInSignupFlow, segments]);

  return (
    <View style={[styles.container, { backgroundColor }]}>
      <ActivityIndicator size="large" color={textColor} />
      <ThemedText style={styles.loadingText}>Loading Kondition...</ThemedText>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
  },
});