import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { apiService, WorkoutResponse } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';

const WorkoutDetailScreen = () => {
  const { workoutId } = useLocalSearchParams<{ workoutId: string }>();
  const { user } = useAuth();
  const [workout, setWorkout] = useState<WorkoutResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (workoutId) {
      fetchWorkoutDetail();
    }
  }, [workoutId]);

  const fetchWorkoutDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const workoutData = await apiService.getWorkoutById(workoutId!);
      setWorkout(workoutData);
    } catch (err) {
      console.error('Error fetching workout detail:', err);
      setError(err instanceof Error ? err.message : 'Failed to load workout details');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDuration = (minutes?: number) => {
    if (!minutes) return 'N/A';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const getCompletionStatus = (workout: WorkoutResponse) => {
    return workout.is_completed ? 'Completed' : 'Incomplete';
  };

  const getStatusColor = (workout: WorkoutResponse) => {
    return workout.is_completed ? '#4CAF50' : '#FF9800';
  };

  const handleGoBack = () => {
    router.back();
  };

  const renderExercise = (exercise: any, index: number) => (
    <View key={exercise.id || index} style={styles.exerciseCard}>
      <View style={styles.exerciseHeader}>
        <Text style={styles.exerciseName}>{exercise.name}</Text>
        <View style={styles.categoryBadge}>
          <Text style={styles.categoryText}>{exercise.category}</Text>
        </View>
      </View>
      
      {exercise.description && (
        <Text style={styles.exerciseDescription}>{exercise.description}</Text>
      )}
      
      <View style={styles.exerciseStats}>
        {exercise.sets && (
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Sets</Text>
            <Text style={styles.statValue}>{exercise.sets}</Text>
          </View>
        )}
        
        {exercise.reps && (
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Reps</Text>
            <Text style={styles.statValue}>{exercise.reps}</Text>
          </View>
        )}
        
        {exercise.weight && (
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Weight</Text>
            <Text style={styles.statValue}>{exercise.weight} kg</Text>
          </View>
        )}
      </View>
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#70A1FF" />
          <Text style={styles.loadingText}>Loading workout details...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error || !workout) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>Unable to Load Workout</Text>
          <Text style={styles.errorMessage}>{error || 'Workout not found'}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={fetchWorkoutDetail}>
            <Text style={styles.retryText}>Try Again</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.backButton} onPress={handleGoBack}>
            <Text style={styles.backText}>Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButtonHeader} onPress={handleGoBack}>
          <Text style={styles.backButtonText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Workout Details</Text>
      </View>

      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Workout Info Card */}
        <View style={styles.workoutInfoCard}>
          <View style={styles.workoutHeader}>
            <Text style={styles.workoutName}>{workout.name}</Text>
            <View style={[styles.statusBadge, { backgroundColor: getStatusColor(workout) }]}>
              <Text style={styles.statusText}>{getCompletionStatus(workout)}</Text>
            </View>
          </View>
          
          <Text style={styles.workoutDate}>
            {workout.completed_date 
              ? `Completed: ${formatDate(workout.completed_date)}`
              : `Created: ${formatDate(workout.created_at)}`
            }
          </Text>
          
          {workout.scheduled_date && (
            <Text style={styles.scheduledDate}>
              Scheduled: {formatDate(workout.scheduled_date)}
            </Text>
          )}
          
          <View style={styles.workoutStats}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Duration</Text>
              <Text style={styles.statValue}>{formatDuration(workout.duration_minutes)}</Text>
            </View>
            
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Exercises</Text>
              <Text style={styles.statValue}>{workout.exercises?.length || 0}</Text>
            </View>
          </View>
          
          {workout.description && (
            <View style={styles.descriptionContainer}>
              <Text style={styles.descriptionLabel}>Description:</Text>
              <Text style={styles.workoutDescription}>{workout.description}</Text>
            </View>
          )}
        </View>

        {/* Exercises Section */}
        <View style={styles.exercisesSection}>
          <Text style={styles.sectionTitle}>
            Exercises ({workout.exercises?.length || 0})
          </Text>
          
          {workout.exercises && workout.exercises.length > 0 ? (
            workout.exercises.map(renderExercise)
          ) : (
            <View style={styles.noExercisesContainer}>
              <Text style={styles.noExercisesText}>No exercises recorded for this workout</Text>
            </View>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#F8F9FA',
    borderBottomWidth: 1,
    borderBottomColor: '#E9ECEF',
  },
  backButtonHeader: {
    marginRight: 16,
  },
  backButtonText: {
    fontSize: 16,
    color: '#70A1FF',
    fontWeight: '600',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 80,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FF6B6B',
    marginBottom: 8,
  },
  errorMessage: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 24,
  },
  retryButton: {
    backgroundColor: '#70A1FF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
    marginBottom: 12,
  },
  retryText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  backButton: {
    backgroundColor: '#E9ECEF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
  },
  backText: {
    color: '#333',
    fontSize: 16,
    fontWeight: '600',
  },
  workoutInfoCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#F0F0F0',
  },
  workoutHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  workoutName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
    marginRight: 12,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  statusText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  workoutDate: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  scheduledDate: {
    fontSize: 14,
    color: '#999',
    marginBottom: 16,
  },
  workoutStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 14,
    color: '#999',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  descriptionContainer: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#F0F0F0',
  },
  descriptionLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  workoutDescription: {
    fontSize: 16,
    color: '#666',
    lineHeight: 24,
  },
  exercisesSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  exerciseCard: {
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E9ECEF',
  },
  exerciseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  exerciseName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
    marginRight: 12,
  },
  categoryBadge: {
    backgroundColor: '#70A1FF',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  categoryText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  exerciseDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    fontStyle: 'italic',
  },
  exerciseStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  noExercisesContainer: {
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
  },
  noExercisesText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
});

export default WorkoutDetailScreen;