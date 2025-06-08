import React, { createContext, useContext, useState, ReactNode } from 'react';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext'; // adjust if needed

export interface Exercise {
  id: string;
  workout_id: string;
  name: string;
  description?: string;
  muscle_group: string;
  category: string;
  sets?: number;
  reps?: number;
  weight?: number; 
  created_at: Date;
  updated_at?: Date;
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
  exercises: Exercise[]; //This won't be updated, instead use id to retrieve all exercises for a related workout
  duration: number; // in minutes
  notes?: string;
}

interface WorkoutContextType {
  workouts: Workout[];
  exercises: Exercise[];
  currentWorkout: Workout | null;
  exerSets: number;
  exerReps: number;
  exerWeights: number;
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
  getExercises: (workoutID: string) => void;
  getExercises_2: () => Exercise[];
}

const WorkoutContext = createContext<WorkoutContextType | undefined>(undefined);

export const WorkoutProvider = ({ children }: { children: ReactNode }) => {
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [currentWorkout, setCurrentWorkout] = useState<Workout | null>(null);
  const { token, isAuthenticated, isLoading } = useAuth(); //token of user
  const [exerSets, setExerSets] = useState(0);
  const [exerReps, setExerReps] = useState(0);
  const [exerWeights, setExerWeights] = useState(0);


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
      //await getExercises(.id);
    } catch (error) {
      console.error('Failed to load workouts:', error.response?.data || error.message);
    }
  };
  const endWorkout = async (updatedWorkout: Workout) => {
    await addWorkout(updatedWorkout);
    setCurrentWorkout(null);
  };

  const getExercises = async (workoutID: string) => {
    try{
      const exerReq = 'http://localhost:8000/api/v1/workouts/' + workoutID + '/exercises';
      const response = await axios.get(exerReq, {
        headers: {
          Authorization: `Bearer ${token}`,
        },        
      });

      //console.log("getExercises response: ", response);
      setExercises(response.data);
      for (const ex of exercises) {
        setExerSets(exerSets + ex.sets);
        setExerReps(exerReps + ex.reps);
        setExerWeights(exerWeights + ex.weight);
      }
      console.log(exercises);
      console.log(exerSets);
    } catch (error){
      console.log("Failed to get exercises for associated ID ", workoutID, ". ", error.response?.data || error.message)
    }
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
      exerSets,
      exerReps,
      exerWeights,
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
      getExercises,
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