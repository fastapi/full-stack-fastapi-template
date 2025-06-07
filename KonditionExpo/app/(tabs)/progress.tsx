import React, { useState, useEffect } from 'react';
import { 
  SafeAreaView, 
  View, 
  Text, 
  StyleSheet, 
  ScrollView, 
  TouchableOpacity, 
  Modal,
  Alert,
  Dimensions 
} from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import { useWorkout, Workout } from '@/contexts/WorkoutContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { router } from 'expo-router';
import { useAuth } from '@/contexts/AuthContext';
const { width } = Dimensions.get('window');

interface WorkoutItemProps {
  workout: Workout;
  onPress: () => void;
}

const WorkoutItem = ({ workout, onPress }: WorkoutItemProps) => {
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric' 
    });
  };

  console.log("Workout Item: ", workout);

  return (
    <TouchableOpacity style={styles.workoutItem} onPress={onPress}>
      <View style={styles.workoutHeader}>
        <Text style={styles.workoutName}>{workout.name}</Text>
        <Text style={styles.workoutDate}>{formatDate(workout.date)}</Text>
      </View>
      <View style={styles.workoutStats}>
        <Text style={styles.workoutStat}>{workout.exercises.sets} sets</Text>
        <Text style={styles.workoutStat}>{workout.exercises.reps} reps</Text>
        <Text style={styles.workoutStat}>{workout.exercises.weight} weight</Text>
      </View>
    </TouchableOpacity>
  );
};



const ProgressScreen = () => {
  const { workouts, currentWorkout, startWorkout, getWorkouts } = useWorkout();
  const { isAuthenticated, isLoading } = useAuth();
  const [showNewWorkoutModal, setShowNewWorkoutModal] = useState(false);
  const [newWorkoutName, setNewWorkoutName] = useState('');
  const backgroundColor = '#FFFFFF';
  const textColor = '#333';
  const tintColor = '#70A1FF';
  
  // ⬇️ Load backend workouts once auth is ready
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      console.log("Authenticated and loaded in workout context, about to get workouts!")
      getWorkouts();
    }
  }, [isAuthenticated, isLoading]);

  if (isLoading || !isAuthenticated) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={{ textAlign: 'center', marginTop: 100 }}>Loading your progress...</Text>
      </SafeAreaView>
    );
  }

  const handleStartWorkout = () => {
    if (!newWorkoutName.trim()) {
      Alert.alert('Error', 'Please enter a workout name');
      return;
    }
    startWorkout(newWorkoutName.trim());
    setNewWorkoutName('');
    setShowNewWorkoutModal(false);
    router.push('../workout');
  };

  const getWeeklyWorkouts = () => {
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return date.toDateString();
    });

    return last7Days.map(dateString => {
      const workoutsOnDay = workouts.filter(w => 
        w.date.toDateString() === dateString
      );
      return workoutsOnDay.length;
    });
  };

  const getWeeklyLabels = () => {
    return Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return date.toLocaleDateString('en-US', { weekday: 'short' });
    });
  };

  const getTotalWorkouts = () => workouts.length;
  const getThisWeekWorkouts = () => {
    const startOfWeek = new Date();
    startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay());
    return workouts.filter(w => w.date >= startOfWeek).length;
  };

  const getAverageWorkoutDuration = () => {
    if (workouts.length === 0) return 0;
    const total = workouts.reduce((sum, w) => sum + w.duration, 0);
    return Math.round(total / workouts.length);
  };

  const weeklyData = getWeeklyWorkouts();
  const weeklyLabels = getWeeklyLabels();

  return (
    <SafeAreaView style={[styles.container, { backgroundColor }]}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={[styles.headerTitle, { color: textColor }]}>Progress</Text>
          <Text style={[styles.headerSubtitle, { color: textColor }]}>
            Track your fitness journey
          </Text>
        </View>

        {/* Current Workout Banner */}
        {currentWorkout && (
          <View style={[styles.currentWorkoutBanner, { backgroundColor: tintColor }]}>
            <Text style={styles.currentWorkoutText}>
              Workout in Progress: {currentWorkout.name}
            </Text>
            <TouchableOpacity 
              style={styles.continueBtn}
              onPress={() => router.push('../workout')}
            >
              <Text style={styles.continueBtnText}>Continue</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{getTotalWorkouts()}</Text>
            <Text style={styles.statLabel}>Total Workouts</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{getThisWeekWorkouts()}</Text>
            <Text style={styles.statLabel}>This Week</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{getAverageWorkoutDuration()}</Text>
            <Text style={styles.statLabel}>Avg Duration</Text>
          </View>
        </View>

        {/* Weekly Chart */}
        {workouts.length > 0 && (
          <View style={styles.chartContainer}>
            <Text style={[styles.sectionTitle, { color: textColor }]}>
              Weekly Activity
            </Text>
            <LineChart
              data={{
                labels: weeklyLabels,
                datasets: [
                  {
                    data: weeklyData,
                    color: () => tintColor,
                    strokeWidth: 2,
                  },
                ],
              }}
              width={width - 64}
              height={200}
              chartConfig={{
                backgroundGradientFrom: backgroundColor,
                backgroundGradientTo: backgroundColor,
                color: () => tintColor,
                strokeWidth: 2,
                decimalPlaces: 0,
              }}
              bezier
              style={styles.chart}
            />
          </View>
        )}

        {/* Start New Workout Button */}
        <View style={styles.actionContainer}>
          <Button
            title="Start New Workout"
            onPress={() => setShowNewWorkoutModal(true)}
            size="lg"
            fullWidth
            style={styles.startWorkoutBtn}
          />
        </View>

        {/* Recent Workouts */}
        <View style={styles.workoutHistoryContainer}>
          <Text style={[styles.sectionTitle, { color: textColor }]}>
            Recent Workouts
          </Text>
          {workouts.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={[styles.emptyStateText, { color: textColor }]}>
                No workouts yet. Start your first workout to track your progress!
              </Text>
            </View>
          ) : ( 
            workouts
              .sort((a, b) => b.date.getTime() - a.date.getTime())
              .slice(0, 3) // Should prob just be 3 
              .map((workout) => (
                <WorkoutItem
                  key={workout.id}
                  workout={workout}
                  onPress={() => {/* Navigate to workout details */}}
                />
              ))
          )}
        </View>
      </ScrollView>

      {/* New Workout Modal */}
      <Modal
        visible={showNewWorkoutModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowNewWorkoutModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor }]}>
            <Text style={[styles.modalTitle, { color: textColor }]}>
              Start New Workout
            </Text>
            <Input
              label="Workout Name"
              value={newWorkoutName}
              onChangeText={setNewWorkoutName}
              placeholder="e.g., Push Day, Leg Day, Cardio"
              style={styles.modalInput}
            />
            <View style={styles.modalButtons}>
              <Button
                title="Cancel"
                variant="outline"
                onPress={() => {
                  setShowNewWorkoutModal(false);
                  setNewWorkoutName('');
                }}
                style={styles.modalButton}
              />
              <Button
                title="Start"
                onPress={handleStartWorkout}
                style={styles.modalButton}
              />
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  content: {
    padding: 20,
    paddingBottom: 100,
  },
  header: {
    marginBottom: 20,
    paddingTop: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#333',
  },
  headerSubtitle: {
    fontSize: 16,
    opacity: 0.7,
    color: '#666',
  },
  currentWorkoutBanner: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#B07FFD',
  },
  currentWorkoutText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    flex: 1,
  },
  continueBtn: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  continueBtnText: {
    color: 'white',
    fontWeight: '600',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  statCard: {
    backgroundColor: '#E5F1FF',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 4,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#555',
    textAlign: 'center',
  },
  chartContainer: {
    marginBottom: 20,
    backgroundColor: '#F0F6FF',
    borderRadius: 16,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333',
  },
  chart: {
    borderRadius: 12,
  },
  actionContainer: {
    marginBottom: 20,
  },
  startWorkoutBtn: {
    marginBottom: 10,
    backgroundColor: '#70A1FF',
  },
  workoutHistoryContainer: {
    marginBottom: 20,
  },
  workoutItem: {
    backgroundColor: '#F9FAFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5F1FF',
  },
  workoutHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  workoutName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  workoutDate: {
    fontSize: 12,
    color: '#666',
  },
  workoutStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  workoutStat: {
    fontSize: 12,
    color: '#666',
  },
  emptyState: {
    padding: 40,
    alignItems: 'center',
    backgroundColor: '#F5F8FF',
    borderRadius: 16,
    marginVertical: 20,
  },
  emptyStateText: {
    fontSize: 16,
    textAlign: 'center',
    opacity: 0.6,
    color: '#666',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    width: '90%',
    padding: 20,
    borderRadius: 12,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    backgroundColor: '#FFFFFF',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
    color: '#333',
  },
  modalInput: {
    marginBottom: 20,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  modalButton: {
    flex: 1,
    marginHorizontal: 5,
  },
});

export default ProgressScreen; 