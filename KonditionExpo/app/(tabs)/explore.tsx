import { StyleSheet, ScrollView, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { useThemeColor } from '@/hooks/useThemeColor';

interface FeatureItemProps {
  number: number;
  title: string;
  icon: keyof typeof Ionicons.glyphMap;
}

const FeatureItem = ({ number, title, icon }: FeatureItemProps) => {
  const tintColor = useThemeColor({}, 'tint');
  
  return (
    <ThemedView style={styles.featureItem}>
      <View style={[styles.featureNumberContainer, { backgroundColor: tintColor }]}>
        <ThemedText style={styles.featureNumber}>{number}</ThemedText>
      </View>
      <View style={styles.featureContent}>
        <ThemedText type="subtitle" style={styles.featureTitle}>{title}</ThemedText>
        <Ionicons name={icon} size={24} color={tintColor} style={styles.featureIcon} />
      </View>
    </ThemedView>
  );
};

export default function ExploreScreen() {
  const backgroundColor = useThemeColor({}, 'background');
  
  return (
    <ScrollView style={[styles.container, { backgroundColor }]}>
      <ThemedView style={styles.headerContainer}>
        <ThemedText type="title" style={styles.headerTitle}>
          FEATURES
        </ThemedText>
        <ThemedText style={styles.headerSubtitle}>
          Explore all the features Kondition has to offer
        </ThemedText>
      </ThemedView>

      <FeatureItem 
        number={1} 
        title="WORKOUT PLANS" 
        icon="fitness-outline" 
      />
      
      <FeatureItem 
        number={2} 
        title="NUTRITION TRACKING" 
        icon="nutrition-outline" 
      />
      
      <FeatureItem 
        number={3} 
        title="PROGRESS ANALYTICS" 
        icon="analytics-outline" 
      />
      
      <FeatureItem 
        number={4} 
        title="COMMUNITY SUPPORT" 
        icon="people-outline" 
      />
      
      <FeatureItem 
        number={5} 
        title="PERSONALIZED GOALS" 
        icon="trophy-outline" 
      />
      
      <FeatureItem 
        number={6} 
        title="VIDEO TUTORIALS" 
        icon="videocam-outline" 
      />
      
      <FeatureItem 
        number={7} 
        title="WORKOUT REMINDERS" 
        icon="alarm-outline" 
      />
      
      <FeatureItem 
        number={8} 
        title="EQUIPMENT GUIDE" 
        icon="barbell-outline" 
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  headerContainer: {
    padding: 20,
    paddingTop: 60,
    alignItems: 'center',
    marginBottom: 20,
  },
  headerTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: 16,
    textAlign: 'center',
    opacity: 0.8,
    marginBottom: 10,
  },
  featureItem: {
    marginHorizontal: 20,
    marginBottom: 16,
    borderRadius: 12,
    overflow: 'hidden',
  },
  featureNumberContainer: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  featureNumber: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 18,
  },
  featureContent: {
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  featureTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  featureIcon: {
    marginLeft: 8,
  },
});
