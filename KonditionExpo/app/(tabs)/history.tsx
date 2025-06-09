import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { router } from 'expo-router';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';

export type Exercise = {
  id: string;
  name: string;
  sets?: number;
  reps?: number;
  weight?: number;
  category: string;
};

export type WorkoutResponse = {
  id: string;
  name: string;
  description?: string;
  is_completed: boolean;
  created_at: string;
  completed_date?: string;
  duration_minutes?: number;
  scheduled_date?: number;
  exercises: Exercise[];  // <-- include this
};

const WorkoutHistoryScreen = () => {
  const { user } = useAuth();
  const [workouts, setWorkouts] = useState<WorkoutResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token, isAuthenticated, isLoading } = useAuth(); //token of user

  const fetchWorkouts = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      //const workoutData = await apiService.getWorkouts(); - Uses old api.ts, idk

      const response = await axios.get('http://localhost:8000/api/v1/workouts/exercises/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      console.log("Fetched workouts for history: ", response);
      const workoutData = response.data;
      // Ensure workoutData is an array
      if (Array.isArray(workoutData)) {
        setWorkouts(workoutData);
      } else {
        console.warn('API returned non-array data:', workoutData);
        setWorkouts([]);
        setError('Invalid data format received from server');
      }
    } catch (err) {
      console.error('Error fetching workouts:', err);
      setError(err instanceof Error ? err.message : 'Failed to load workouts');
      setWorkouts([]); // Ensure workouts is always an array
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchWorkouts();
  }, []);

  const onRefresh = () => {
    fetchWorkouts(true);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatDuration = (workout: WorkoutResponse): string => {
    if (!workout.is_completed) return 'N/A';
  
    const start = workout.scheduled_date ? new Date(workout.scheduled_date) : null;
    const end = workout.completed_date ? new Date(workout.completed_date) : null;
  
    if (!start || !end || isNaN(start.getTime()) || isNaN(end.getTime())) return 'N/A';
  
    const diffMs = end.getTime() - start.getTime();
    if (diffMs <= 0) return 'N/A';
  
    const totalSeconds = Math.floor(diffMs / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
  
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  };
  

  const getCompletionStatus = (workout: WorkoutResponse) => {
    return workout.is_completed ? 'Completed' : 'Incomplete';
  };

  const getStatusColor = (workout: WorkoutResponse) => {
    return workout.is_completed ? '#4CAF50' : '#FF9800';
  };

  /*const handleWorkoutPress = (workout: WorkoutResponse) => {
    // Navigate to the detailed workout view
    router.push({
      pathname: '/workout-detail',
      params: { workoutId: workout.id }
    });
  }; Not needed */

  const renderWorkoutItem = (workout: WorkoutResponse) => (
    <View key={workout.id} style={styles.workoutCard}>
      {/* Workout Header */}
      <View style={styles.workoutHeader}>
        <Text style={styles.workoutName}>{workout.name}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(workout) }]}>
          <Text style={styles.statusText}>{getCompletionStatus(workout)}</Text>
        </View>
      </View>
  
      {/* Workout Date */}
      <Text style={styles.workoutDate}>
        {formatDate(workout.completed_date || workout.created_at)}
      </Text>
  
      {/* Workout Metadata */}
      <View style={styles.workoutDetails}>
  <View style={styles.detailItem}>
    <Text style={styles.detailLabel}>Duration</Text>
    <Text style={styles.detailValue}>{formatDuration(workout)}</Text>
  </View>
  
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>Exercises</Text>
          <Text style={styles.detailValue}>{workout.exercises?.length || 0}</Text>
        </View>
      </View>
  
      {/* Workout Description */}
      {workout.description && (
        <Text style={styles.workoutDescription} numberOfLines={2}>
          {workout.description}
        </Text>
      )}
  
      {/* Exercise List */}
      {workout.exercises?.length > 0 && (
        <View style={{ marginTop: 12 }}>
          <Text style={{ fontWeight: '600', color: '#444', marginBottom: 4 }}>Exercises:</Text>
          {workout.exercises.map((ex) => (
            <View key={ex.id} style={{ marginBottom: 6, paddingLeft: 8 }}>
              <Text style={{ color: '#333' }}>
                • {ex.name} — {ex.sets || 0} × {ex.reps || 0} @ {ex.weight || 0} lbs
              </Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
  
  

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Text style={styles.emptyTitle}>No Workouts Yet</Text>
      <Text style={styles.emptyMessage}>
        Start your fitness journey by completing your first workout!
      </Text>
    </View>
  );

  const renderErrorState = () => (
    <View style={styles.errorState}>
      <Text style={styles.errorTitle}>Unable to Load Workouts</Text>
      <Text style={styles.errorMessage}>{error}</Text>
      <TouchableOpacity style={styles.retryButton} onPress={() => fetchWorkouts()}>
        <Text style={styles.retryText}>Try Again</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading && !refreshing) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#70A1FF" />
          <Text style={styles.loadingText}>Loading workout history...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Workout History</Text>
        <Text style={styles.headerSubtitle}>
          {workouts.length} Total —{" "}
          {workouts.filter(w => !w.is_completed).length} In Progress —{" "}
          {workouts.filter(w => w.is_completed).length} Finished
        </Text>
      </View>


      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {error ? (
          renderErrorState()
        ) : !Array.isArray(workouts) || workouts.length === 0 ? (
          renderEmptyState()
        ) : (
          [...workouts]
        .sort((a, b) => {
          // 1. Completed workouts first
          if (a.is_completed !== b.is_completed) {
            return b.is_completed ? 1 : -1;
          }

          // 2. Then sort by date (fallback to created_at if completed_date is missing)
          const aDate = new Date(a.completed_date || a.created_at).getTime();
          const bDate = new Date(b.completed_date || b.created_at).getTime();
          return bDate - aDate;
        })
        .map(renderWorkoutItem)
        )}
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
    padding: 20,
    backgroundColor: '#F8F9FA',
    borderBottomWidth: 1,
    borderBottomColor: '#E9ECEF',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#666',
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
  workoutCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
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
    marginBottom: 8,
  },
  workoutName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
    marginRight: 12,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  workoutDate: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  workoutDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  detailItem: {
    flex: 1,
  },
  detailLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 2,
  },
  detailValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  workoutDescription: {
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
    marginTop: 8,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  emptyMessage: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
  errorState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
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
  },
  retryText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  viewDetailsContainer: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#F0F0F0',
    alignItems: 'center',
  },
  viewDetailsText: {
    fontSize: 14,
    color: '#70A1FF',
    fontWeight: '600',
  },
});

export default WorkoutHistoryScreen;