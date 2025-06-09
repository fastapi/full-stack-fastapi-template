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
  TextInput,
} from 'react-native';
import { router } from 'expo-router';
import { useWorkout, Exercise, WorkoutSet } from '@/contexts/WorkoutContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

// Predefined exercises database
const EXERCISES: Exercise[] = [
  { id: '1', name: 'Bench Press', muscle_group: 'Chest', type: 'strength' },
  { id: '2', name: 'Squat', muscle_group: 'Legs', type: 'strength' },
  { id: '3', name: 'Deadlift', muscle_group: 'Back', type: 'strength' },
  { id: '4', name: 'Pull-ups', muscle_group: 'Back', type: 'strength' },
  { id: '5', name: 'Push-ups', muscle_group: 'Chest', type: 'strength' },
  { id: '6', name: 'Shoulder Press', muscle_group: 'Shoulders', type: 'strength' },
  { id: '7', name: 'Bicep Curls', muscle_group: 'Arms', type: 'strength' },
  { id: '8', name: 'Tricep Dips', muscle_group: 'Arms', type: 'strength' },
  { id: '9', name: 'Lunges', muscle_group: 'Legs', type: 'strength' },
  { id: '10', name: 'Plank', muscle_group: 'Core', type: 'strength' },
  { id: '11', name: 'Running', muscle_group: 'Cardio', type: 'cardio' },
  { id: '12', name: 'Cycling', muscle_group: 'Cardio', type: 'cardio' },
];

interface SetRowProps {
  set: WorkoutSet;
  setNumber: number;
  onUpdate: (updatedSet: Partial<WorkoutSet>) => void;
  onRemove: () => void;
}

const SetRow = ({ set, setNumber, onUpdate, onRemove }: SetRowProps) => {
  return (
    <View style={styles.setRow}>
      <Text style={styles.setNumber}>{setNumber}</Text>

      <View style={styles.inputGroup}>
        <TextInput
          style={styles.setInput}
          value={set.weight.toString()}
          onChangeText={(text) => onUpdate({ weight: parseInt(text) || 0 })}
          placeholder="Weight"
          keyboardType="numeric"
        />
        <Text style={styles.inputUnit}>kg</Text>
      </View>

      <View style={styles.inputGroup}>
        <TextInput
          style={styles.setInput}
          value={set.reps.toString()}
          onChangeText={(text) => onUpdate({ reps: parseInt(text) || 0 })}
          placeholder="Reps"
          keyboardType="numeric"
        />
        <Text style={styles.inputUnit}>reps</Text>
      </View>

      <TouchableOpacity onPress={onRemove} style={styles.removeButton}>
        <Text style={styles.removeButtonText}>×</Text>
      </TouchableOpacity>
    </View>
  );
};


interface ExerciseCardProps {
  workoutExercise: any;
  onAddSet: () => void;
  onUpdateSet: (setId: string, updatedSet: Partial<WorkoutSet>) => void;
  onRemoveSet: (setId: string) => void;
}

const ExerciseCard = ({ workoutExercise, onAddSet, onUpdateSet, onRemoveSet }: ExerciseCardProps) => {
  return (
    <View style={styles.exerciseCard}>
      <View style={styles.exerciseHeader}>
        <Text style={styles.exerciseName}>{workoutExercise.exercise.name}</Text>
        <Text style={styles.muscleGroup}>{workoutExercise.exercise.muscle_group}</Text>
      </View>
      
      <View style={styles.setsContainer}>
        <View style={styles.setHeaderRow}>
          <Text style={styles.setHeaderText}>Set</Text>
          <Text style={styles.setHeaderText}>Weight</Text>
          <Text style={styles.setHeaderText}>Reps</Text>
          <Text style={styles.setHeaderText}></Text>
        </View>
        
        {workoutExercise.sets.map((set: WorkoutSet, index: number) => (
          <SetRow
            key={set.id}
            set={set}
            setNumber={index + 1}
            onUpdate={(updatedSet) => onUpdateSet(set.id, updatedSet)}
            onRemove={() => onRemoveSet(set.id)}
          />
        ))}
        
        <Button
          title="Add Set"
          variant="outline"
          onPress={onAddSet}
          style={styles.addSetButton}
        />
      </View>
    </View>
  );
};

const WorkoutScreen = () => {
  const { 
    currentWorkout, 
    endWorkout, 
    addExerciseToCurrentWorkout, 
    addSetToExercise, 
    removeSetFromExercise, 
    updateSet 
  } = useWorkout();
  
  const [showExerciseModal, setShowExerciseModal] = useState(false);
  const [filteredExercises, setFilteredExercises] = useState(EXERCISES);
  const [searchQuery, setSearchQuery] = useState('');
  const [startTime] = useState(new Date());
  
  useEffect(() => {
    if (!currentWorkout) {
      router.replace('/(tabs)');
    }
  }, [currentWorkout]);

  useEffect(() => {
    const filtered = EXERCISES.filter(exercise =>
      exercise.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      exercise.muscle_group.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredExercises(filtered);
  }, [searchQuery]);

  const handleAddExercise = (exercise: Exercise) => {
    addExerciseToCurrentWorkout(exercise);
    setShowExerciseModal(false);
    setSearchQuery('');
  };

  const handleAddSet = (exerciseId: string) => {
    const newSet = { reps: 0, weight: 0 };
    addSetToExercise(exerciseId, newSet);
  };

  const handleFinishWorkout = async () => {
    if (!currentWorkout) return;
  
    const duration = Math.round((new Date().getTime() - startTime.getTime()) / 60000);
    const updatedWorkout = { ...currentWorkout, duration };
  
    console.log("FinishWorkout-UpdatedWorkout: ", updatedWorkout);
  
    try {
      await endWorkout(updatedWorkout); // wait for backend POST to complete
      router.replace('/(tabs)');
    } catch (error) {
      console.error("Error finishing workout:", error);
      // Optionally show UI feedback
    }
  };

  if (!currentWorkout) {
    return null;
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: '#FFFFFF' }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.replace('/(tabs)')}>
          <Text style={[styles.backButton, { color: '#70A1FF' }]}>← Exit</Text>
        </TouchableOpacity>
        <Text style={[styles.workoutTitle, { color: '#333' }]}>{currentWorkout.name}</Text>
        <TouchableOpacity onPress={handleFinishWorkout}>
          <Text style={[styles.finishButton, { color: '#70A1FF' }]}>Finish</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {currentWorkout.exercises.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={[styles.emptyStateText, { color: '#666' }]}>
              No exercises added yet. Add your first exercise to get started!
            </Text>
          </View>
        ) : (
          currentWorkout.exercises.map((workoutExercise) => (
            <ExerciseCard
              key={workoutExercise.id}
              workoutExercise={workoutExercise}
              onAddSet={() => handleAddSet(workoutExercise.id)}
              onUpdateSet={(setId, updatedSet) => updateSet(workoutExercise.id, setId, updatedSet)}
              onRemoveSet={(setId) => removeSetFromExercise(workoutExercise.id, setId)}
            />
          ))
        )}

        <Button
          title="Add Exercise"
          onPress={() => setShowExerciseModal(true)}
          style={styles.addExerciseButton}
          size="lg"
          fullWidth
        />
      </ScrollView>

      {/* Exercise Selection Modal */}
      <Modal
        visible={showExerciseModal}
        animationType="slide"
        onRequestClose={() => setShowExerciseModal(false)}
      >
        <SafeAreaView style={[styles.modalContainer, { backgroundColor: '#FFFFFF' }]}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowExerciseModal(false)}>
              <Text style={[styles.modalCloseButton, { color: '#70A1FF' }]}>Cancel</Text>
            </TouchableOpacity>
            <Text style={[styles.modalTitle, { color: '#333' }]}>Select Exercise</Text>
            <View style={{ width: 60 }} />
          </View>

          <Input
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholder="Search exercises..."
            style={styles.searchInput}
          />

          <ScrollView style={styles.exerciseList}>
            {filteredExercises.map((exercise) => (
              <TouchableOpacity
                key={exercise.id}
                style={styles.exerciseItem}
                onPress={() => handleAddExercise(exercise)}
              >
                <View>
                  <Text style={styles.exerciseItemName}>{exercise.name}</Text>
                  <Text style={styles.exerciseItemMuscle}>{exercise.muscle_group}</Text>
                </View>
                <Text style={[styles.exerciseItemType, { color: '#B07FFD' }]}>
                  {exercise.type}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </SafeAreaView>
      </Modal>
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
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5F1FF',
    backgroundColor: '#F9FAFF',
  },
  backButton: {
    fontSize: 16,
    fontWeight: '600',
    color: '#70A1FF',
  },
  workoutTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  finishButton: {
    fontSize: 16,
    fontWeight: '600',
    color: '#70A1FF',
  },
  content: {
    flex: 1,
    padding: 16,
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
  exerciseCard: {
    backgroundColor: '#E5F1FF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#A3C9FD',
  },
  exerciseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  exerciseName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  muscleGroup: {
    fontSize: 14,
    color: '#666',
    backgroundColor: '#F0F6FF',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  setsContainer: {
    marginTop: 8,
  },
  setHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 4,
    marginBottom: 8,
    backgroundColor: '#F0F6FF',
    borderRadius: 8,
  },
  setHeaderText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#555',
    flex: 1,
    textAlign: 'center',
  },
  setRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 4,
    marginBottom: 8,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5F1FF',
  },
  inputLabel: {
    fontSize: 12,
    color: '#666',
    marginRight: 8,
  },
  removeButton: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#FF6B9D',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  removeButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  addSetButton: {
    marginTop: 8,
    backgroundColor: '#70A1FF',
  },
  addExerciseButton: {
    marginTop: 20,
    marginBottom: 40,
    backgroundColor: '#70A1FF',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5F1FF',
    backgroundColor: '#F9FAFF',
  },
  modalCloseButton: {
    fontSize: 16,
    fontWeight: '600',
    color: '#70A1FF',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  searchInput: {
    margin: 16,
  },
  exerciseList: {
    flex: 1,
    paddingHorizontal: 16,
  },
  exerciseItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#F0F6FF',
    borderRadius: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#E5F1FF',
  },
  exerciseItemName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  exerciseItemMuscle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  exerciseItemType: {
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
    color: '#B07FFD',
    backgroundColor: '#F5F8FF',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  setRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 4,
    marginBottom: 8,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5F1FF',
  },
  
  setNumber: {
    width: 30,
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
  },
  
  inputGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 4,
    width: 100, // constrain width for layout stability
  },
  
  setInput: {
    width: 50, // fixed to prevent stretch
    height: 36,
    borderWidth: 1,
    borderColor: '#A3C9FD',
    borderRadius: 8,
    paddingHorizontal: 8,
    fontSize: 14,
    textAlign: 'center',
    backgroundColor: '#fff',
  },
  

  inputUnit: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
    alignSelf: 'center',
  },
  
});

export default WorkoutScreen; 