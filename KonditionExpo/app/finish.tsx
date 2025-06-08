import { useLocalSearchParams, router } from 'expo-router';
import { View, Text, Button } from 'react-native';

export default function FinishWorkoutScreen() {
  const { workoutId } = useLocalSearchParams();

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Finish Workout Screen</Text>
      <Text>Workout ID: {workoutId}</Text>

      <Button title="Back" onPress={() => router.back()} />
    </View>
  );
}
