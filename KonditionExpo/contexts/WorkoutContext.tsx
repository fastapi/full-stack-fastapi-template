import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface Exercise {
  id: string;
  name: string;
  muscle_group: string;
  type: 'strength' | 'cardio' | 'flexibility';
}

export interface WorkoutSet {
  id: string;
  reps: number;
  weight: number; // in kg
  duration?: number; // in seconds for cardio
  distance?: number; // in km for cardio
}

export interface WorkoutExercise {
  id: string;
  exercise: Exercise;
  sets: WorkoutSet[];
  notes?: string;
}

export interface Workout {
  id: string;
  date: Date;
  name: string;
  exercises: WorkoutExercise[];
  duration: number; // in minutes
  notes?: string;
}

interface WorkoutContextType {
  workouts: Workout[];
  currentWorkout: Workout | null;
  addWorkout: (workout: Workout) => void;
  updateWorkout: (workoutId: string, workout: Workout) => void;
  deleteWorkout: (workoutId: string) => void;
  startWorkout: (name: string) => void;
  endWorkout: () => void;
  addExerciseToCurrentWorkout: (exercise: Exercise) => void;
  addSetToExercise: (exerciseId: string, set: Omit<WorkoutSet, 'id'>) => void;
  removeSetFromExercise: (exerciseId: string, setId: string) => void;
  updateSet: (exerciseId: string, setId: string, updatedSet: Partial<WorkoutSet>) => void;
}

const WorkoutContext = createContext<WorkoutContextType | undefined>(undefined);

export const WorkoutProvider = ({ children }: { children: ReactNode }) => {
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [currentWorkout, setCurrentWorkout] = useState<Workout | null>(null);

  const generateId = () => Math.random().toString(36).substr(2, 9);

  const addWorkout = (workout: Workout) => {
    setWorkouts(prev => [...prev, workout]);
  };

  const updateWorkout = (workoutId: string, updatedWorkout: Workout) => {
    setWorkouts(prev => prev.map(w => w.id === workoutId ? updatedWorkout : w));
  };

  const deleteWorkout = (workoutId: string) => {
    setWorkouts(prev => prev.filter(w => w.id !== workoutId));
  };

  const startWorkout = (name: string) => {
    const newWorkout: Workout = {
      id: generateId(),
      date: new Date(),
      name,
      exercises: [],
      duration: 0,
    };
    setCurrentWorkout(newWorkout);
  };

  const endWorkout = () => {
    if (currentWorkout) {
      addWorkout(currentWorkout);
      setCurrentWorkout(null);
    }
  };

  const addExerciseToCurrentWorkout = (exercise: Exercise) => {
    if (!currentWorkout) return;
    
    const workoutExercise: WorkoutExercise = {
      id: generateId(),
      exercise,
      sets: [],
    };
    
    setCurrentWorkout(prev => prev ? {
      ...prev,
      exercises: [...prev.exercises, workoutExercise]
    } : null);
  };

  const addSetToExercise = (exerciseId: string, set: Omit<WorkoutSet, 'id'>) => {
    if (!currentWorkout) return;
    
    const newSet: WorkoutSet = {
      ...set,
      id: generateId(),
    };
    
    setCurrentWorkout(prev => prev ? {
      ...prev,
      exercises: prev.exercises.map(ex => 
        ex.id === exerciseId 
          ? { ...ex, sets: [...ex.sets, newSet] }
          : ex
      )
    } : null);
  };

  const removeSetFromExercise = (exerciseId: string, setId: string) => {
    if (!currentWorkout) return;
    
    setCurrentWorkout(prev => prev ? {
      ...prev,
      exercises: prev.exercises.map(ex => 
        ex.id === exerciseId 
          ? { ...ex, sets: ex.sets.filter(s => s.id !== setId) }
          : ex
      )
    } : null);
  };

  const updateSet = (exerciseId: string, setId: string, updatedSet: Partial<WorkoutSet>) => {
    if (!currentWorkout) return;
    
    setCurrentWorkout(prev => prev ? {
      ...prev,
      exercises: prev.exercises.map(ex => 
        ex.id === exerciseId 
          ? { 
              ...ex, 
              sets: ex.sets.map(s => 
                s.id === setId ? { ...s, ...updatedSet } : s
              )
            }
          : ex
      )
    } : null);
  };

  return (
    <WorkoutContext.Provider value={{
      workouts,
      currentWorkout,
      addWorkout,
      updateWorkout,
      deleteWorkout,
      startWorkout,
      endWorkout,
      addExerciseToCurrentWorkout,
      addSetToExercise,
      removeSetFromExercise,
      updateSet,
    }}>
      {children}
    </WorkoutContext.Provider>
  );
};

export const useWorkout = () => {
  const context = useContext(WorkoutContext);
  if (!context) throw new Error('useWorkout must be used within a WorkoutProvider');
  return context;
}; 