import { Image } from 'expo-image';
import { StyleSheet, View, ScrollView } from 'react-native';
import { router } from 'expo-router';

import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { Button } from '@/components/ui/Button';
import { useThemeColor } from '@/hooks/useThemeColor';

export default function HomeScreen() {
  const handleNavigateToLogin = () => {
    router.replace('../login');
  };
  
  const backgroundColor = useThemeColor({}, 'background');
  
  return (
    <ScrollView style={[styles.container, { backgroundColor }]}>
      {/* Hero Section */}
      <View style={styles.heroContainer}>
        <Image
          source={require('@/assets/images/icon.png')}
          style={styles.logo}
          contentFit="contain"
        />
        <ThemedText type="title" style={styles.appName}>KONDITION</ThemedText>
        <ThemedText style={styles.tagline}>Your Personal Fitness Journey Starts Here</ThemedText>
        
        <Button 
          title="Sign In" 
          onPress={handleNavigateToLogin} 
          size="lg"
          variant="solid"
          style={styles.ctaButton}
        />
      </View>
      
      {/* Final CTA */}
      <ThemedView style={styles.ctaSection}>
        <ThemedText type="subtitle" style={styles.ctaTitle}>Ready to Start Your Fitness Journey?</ThemedText>
        <Button 
          title="Get Started Now" 
          onPress={handleNavigateToLogin} 
          size="lg"
          variant="solid"
          style={styles.ctaButton}
        />
      </ThemedView>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  heroContainer: {
    alignItems: 'center',
    paddingTop: 60,
    paddingBottom: 40,
    paddingHorizontal: 20,
  },
  logo: {
    width: 100,
    height: 100,
    marginBottom: 16,
  },
  appName: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  tagline: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 24,
    maxWidth: '80%',
  },
  ctaButton: {
    width: '80%',
    marginBottom: 40,
  },
  ctaSection: {
    padding: 20,
    alignItems: 'center',
    marginBottom: 40,
  },
  ctaTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
});
