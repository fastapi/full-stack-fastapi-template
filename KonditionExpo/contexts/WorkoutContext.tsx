import React, { createContext, useContext, useState, ReactNode } from 'react';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext'; // adjust if needed

export interface Exercise {
  id: string;
  name: string;
  description?: string;
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
  addWorkout: (workout: Workout) => Promise<void>; // <-- async now
  updateWorkout: (workoutId: string, workout: Workout) => void;
  getWorkouts: () => void;
  deleteWorkout: (workoutId: string) => void;
  startWorkout: (name: string) => void;
  endWorkout: (updatedWorkout: Workout) => Promise<void>; // <-- async now
  addExerciseToCurrentWorkout: (exercise: Exercise) => void;
  addSetToExercise: (exerciseId: string, set: Omit<WorkoutSet, 'id'>) => void;
  removeSetFromExercise: (exerciseId: string, setId: string) => void;
  updateSet: (exerciseId: string, setId: string, updatedSet: Partial<WorkoutSet>) => void;
}

const WorkoutContext = createContext<WorkoutContextType | undefined>(undefined);

export const WorkoutProvider = ({ children }: { children: ReactNode }) => {
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [currentWorkout, setCurrentWorkout] = useState<Workout | null>(null);
  const { token, isAuthenticated, isLoading } = useAuth(); //token of user

  //NO WAIT FOR TOKEN, IS GIVING NULL IN WORKOUT CONTEXT

  //console.log("In WorkoutContext - Current User token is: ", token);

  const generateId = () => Math.random().toString(36).substr(2, 9);

  const transformWorkoutForBackend = (workout: Workout) => ({
    name: workout.name,
    description: workout.notes || null,
    scheduled_date: workout.date.toISOString(),
    duration_minutes: workout.duration,
    exercises: workout.exercises.map(ex => ({
      name: ex.exercise.name,
      description: ex.exercise.description || null,
      category: ex.exercise.muscle_group, // or ex.exercise.type if that's better
      sets: ex.sets.length,
      reps: ex.sets.reduce((sum, s) => sum + (s.reps || 0), 0),
      weight: ex.sets.reduce((max, s) => Math.max(max, s.weight || 0), 0),
    })),
  });

  const addWorkout = async (workout: Workout) => {
    try {
      const payload = transformWorkoutForBackend(workout);
      const response = await axios.post(
        'http://localhost:8000/api/v1/workouts/', // Replace with deployment endpoint
        payload,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      //console.log("Response from POST /workouts: ", response);
      const savedWorkout = response.data;

      const saved = {
        ...response.data,
        date: new Date(response.data.created_at),
        exercises: [], // if backend doesn't return them
        duration: response.data.duration_minutes || 0,
      };
  
      setWorkouts(prev => [...prev, saved]);

    } catch (error) {
      console.error('Failed to save workout to backend:', error.response?.data || error.message);
    }
  };

  const getWorkouts = async () => {
    try {
      console.log("About to get workouts with token: ", token);
      const response = await axios.get('http://localhost:8000/api/v1/workouts/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      //console.log("Get workouts response: ", response);      
      // Extract array properly
      const workoutArray = response.data;
  
      // Convert string dates to Date objects
      const parsed = workoutArray.map((w: any) => ({
        ...w,
        date: new Date(w.created_at),
        exercises: w.exercises || [], // fallback to empty array
        duration: w.duration_minutes || 0,
      }));
  
      setWorkouts(parsed);
    } catch (error) {
      console.error('Failed to load workouts:', error.response?.data || error.message);
    }
  };
  const endWorkout = async (updatedWorkout: Workout) => {
    await addWorkout(updatedWorkout);
    setCurrentWorkout(null);
  };

  //Everything below this is old - only updates local state rather than send backend requests

  const updateWorkout = (workoutId: string, updatedWorkout: Workout) => { //Old
    setWorkouts(prev => prev.map(w => w.id === workoutId ? updatedWorkout : w));
  };

  const deleteWorkout = (workoutId: string) => { // Old
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
      getWorkouts,
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