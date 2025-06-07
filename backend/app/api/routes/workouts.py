import uuid
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException, Query, Path, Body, status
from sqlmodel import Session, select, func

from app.api.deps import CurrentUser, SessionDep
from app.models.token import Message
from app.models.workout import (
    Workout,
    WorkoutCreate,
    WorkoutUpdate,
    WorkoutPublic,
    Exercise,
    ExerciseCreate,
    ExerciseUpdate,
    ExercisePublic,
)
from app.crudFuncs import update_personal_bests_after_workout


router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/", response_model=WorkoutPublic)
def create_workout(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    workout_in: WorkoutCreate
) -> Any:
    workout = Workout(
        user_id=current_user.id,
        name=workout_in.name,
        description=workout_in.description,
        scheduled_date=workout_in.scheduled_date,
        duration_minutes=workout_in.duration_minutes,
        is_completed=False,
        created_at=datetime.utcnow(),
    )

    session.add(workout)
    session.commit()
    session.refresh(workout)

    # Add nested exercises
    for ex in workout_in.exercises:
        exercise = Exercise(
            workout_id=workout.id,
            name=ex.name,
            description=ex.description,
            category=ex.category,
            sets=ex.sets,
            reps=ex.reps,
            weight=ex.weight,
        )
        session.add(exercise)

    session.commit()
    session.refresh(workout)

    # Load exercises manually
    workout.exercises = session.exec(
        select(Exercise).where(Exercise.workout_id == workout.id)
    ).all()

    return workout

@router.get("/", response_model=List[WorkoutPublic])
def get_workouts(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, description="Number of records to skip for pagination"),
    limit: int = Query(100, description="Maximum number of records to return")
) -> Any:
    """
    Get all workouts for the current user.
    
    This endpoint retrieves all workouts created by the current user, with pagination support.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (for pagination)
    
    Returns a list of workouts and the total count.
    """
    # Get count of user's workouts
    count_statement = (
        select(func.count())
        .select_from(Workout)
        .where(Workout.user_id == current_user.id)
    )
    count = session.exec(count_statement).one()
    
    # Get user's workouts with pagination
    statement = (
        select(Workout)
        .where(Workout.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    workouts = session.exec(statement).all()
    
    """# Add exercise count to each workout
    workout_data = []
    workout_list = [] #Actual list of Workout, not just data
    for workout in workouts:
        # Count exercises for this workout
        exercise_count_stmt = (
            select(func.count())
            .select_from(Exercise)
            .where(Exercise.workout_id == workout.id)
        )
        exercise_count = session.exec(exercise_count_stmt).one()
        workout_list.append(workout)
        # Convert to dict and add exercise_count
        workout_dict = workout.model_dump()
        workout_dict["exercise_count"] = exercise_count
        workout_data.append(workout_dict)"""
    
    return workouts


@router.get("/{workout_id}", response_model=WorkoutPublic)
def get_workout(
    workout_id: uuid.UUID = Path(..., description="The ID of the workout to retrieve"),
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Get a specific workout by ID.
    
    This endpoint retrieves a specific workout by its ID, including all exercises
    associated with the workout.
    
    - **workout_id**: The UUID of the workout to retrieve
    
    Returns the workout with its exercises.
    
    Raises:
    - 404: If the workout is not found
    - 403: If the workout doesn't belong to the current user
    """
    workout = session.get(Workout, workout_id)
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return workout


@router.put("/{workout_id}", response_model=WorkoutPublic)
def update_workout(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    workout_id: uuid.UUID = Path(..., description="The ID of the workout to update"),
    workout_in: WorkoutUpdate = Body(
        ...,
        examples=[
            {
                "name": "Updated Strength Training",
                "description": "Updated focus on full body",
                "scheduled_date": "2025-05-21T09:00:00Z",
                "duration_minutes": 75,
                "is_completed": False
            }
        ],
    )
) -> Any:
    """
    Update a workout.
    
    This endpoint allows users to update an existing workout's details.
    
    - **workout_id**: The UUID of the workout to update
    - **name**: Optional. The updated name of the workout
    - **description**: Optional. The updated description
    - **scheduled_date**: Optional. The updated scheduled date
    - **completed_date**: Optional. When the workout was completed
    - **duration_minutes**: Optional. The updated expected duration
    - **is_completed**: Optional. Whether the workout is marked as completed
    
    Returns the updated workout.
    
    Raises:
    - 404: If the workout is not found
    - 403: If the workout doesn't belong to the current user
    """
    workout = session.get(Workout, workout_id)
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    update_dict = workout_in.model_dump(exclude_unset=True)
    
    # Set updated_at timestamp
    update_dict["updated_at"] = datetime.utcnow()
    
    workout.sqlmodel_update(update_dict)
    session.add(workout)
    session.commit()
    session.refresh(workout)
    
    return workout


@router.delete("/{workout_id}", response_model=Message)
def delete_workout(
    workout_id: uuid.UUID = Path(..., description="The ID of the workout to delete"),
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Delete a workout.
    
    This endpoint allows users to delete a workout. All associated exercises will also be deleted.
    
    - **workout_id**: The UUID of the workout to delete
    
    Returns a success message.
    
    Raises:
    - 404: If the workout is not found
    - 403: If the workout doesn't belong to the current user
    """
    workout = session.get(Workout, workout_id)
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    session.delete(workout)
    session.commit()
    
    return Message(message="Workout deleted successfully")

# TODO - Kush, added PB updating, test

@router.post("/{workout_id}/complete", response_model=WorkoutPublic)
def complete_workout(
    workout_id: uuid.UUID = Path(..., description="The ID of the workout to mark as completed"),
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Mark a workout as completed.
    
    This endpoint allows users to mark a workout as completed, setting the completed_date
    to the current time and is_completed to True.
    
    - **workout_id**: The UUID of the workout to mark as completed
    
    Returns the updated workout.
    
    Raises:
    - 404: If the workout is not found
    - 403: If the workout doesn't belong to the current user
    """
    workout = session.get(Workout, workout_id)
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    workout.is_completed = True
    workout.completed_date = datetime.utcnow()
    workout.updated_at = datetime.utcnow()
    
    session.add(workout)
    session.commit()
    session.refresh(workout)

    #added for updating personalbests
    update_personal_bests_after_workout(session=session, workout=workout)

    
    return workout


@router.get("/scheduled", response_model=List[WorkoutPublic])
def get_scheduled_workouts(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, description="Number of records to skip for pagination"),
    limit: int = Query(100, description="Maximum number of records to return")
) -> Any:
    """
    Get upcoming scheduled workouts.
    
    This endpoint retrieves all scheduled workouts for the current user that have not been
    completed yet, ordered by scheduled date.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (for pagination)
    
    Returns a list of upcoming workouts and the total count.
    """
    # Get count of user's scheduled workouts
    count_statement = (
        select(func.count())
        .select_from(Workout)
        .where(Workout.user_id == current_user.id)
        .where(Workout.is_completed == False)
        .where(Workout.scheduled_date != None)
        .where(Workout.scheduled_date >= datetime.utcnow())
    )
    count = session.exec(count_statement).one()
    
    # Get user's scheduled workouts with pagination
    statement = (
        select(Workout)
        .where(Workout.user_id == current_user.id)
        .where(Workout.is_completed == False)
        .where(Workout.scheduled_date != None)
        .where(Workout.scheduled_date >= datetime.utcnow())
        .order_by(Workout.scheduled_date)
        .offset(skip)
        .limit(limit)
    )
    workouts = session.exec(statement).all()
    
    return workouts #Maybe check if list?


@router.get("/completed", response_model=List[WorkoutPublic])
def get_completed_workouts(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(0, description="Number of records to skip for pagination"),
    limit: int = Query(100, description="Maximum number of records to return")
) -> Any:
    """
    Get completed workouts.
    
    This endpoint retrieves all completed workouts for the current user,
    ordered by completed date (most recent first).
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (for pagination)
    
    Returns a list of completed workouts and the total count.
    """
    # Get count of user's completed workouts
    count_statement = (
        select(func.count())
        .select_from(Workout)
        .where(Workout.user_id == current_user.id)
        .where(Workout.is_completed == True)
    )
    count = session.exec(count_statement).one()
    
    # Get user's completed workouts with pagination
    statement = (
        select(Workout)
        .where(Workout.user_id == current_user.id)
        .where(Workout.is_completed == True)
        .order_by(Workout.completed_date.desc())
        .offset(skip)
        .limit(limit)
    )
    workouts = session.exec(statement).all()
    
    return workouts


@router.get("/stats", response_model=dict)
def get_workout_stats(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get workout statistics.
    
    This endpoint provides statistics about the user's workouts, including:
    - Total number of workouts
    - Number of completed workouts
    - Number of scheduled workouts
    - Total workout duration (in minutes)
    - Average workout duration (in minutes)
    
    Returns a dictionary with the statistics.
    """
    # Total workouts
    total_workouts_stmt = (
        select(func.count())
        .select_from(Workout)
        .where(Workout.user_id == current_user.id)
    )
    total_workouts = session.exec(total_workouts_stmt).one()
    
    # Completed workouts
    completed_workouts_stmt = (
        select(func.count())
        .select_from(Workout)
        .where(Workout.user_id == current_user.id)
        .where(Workout.is_completed == True)
    )
    completed_workouts = session.exec(completed_workouts_stmt).one()
    
    # Scheduled workouts
    scheduled_workouts_stmt = (
        select(func.count())
        .select_from(Workout)
        .where(Workout.user_id == current_user.id)
        .where(Workout.is_completed == False)
        .where(Workout.scheduled_date != None)
        .where(Workout.scheduled_date >= datetime.utcnow())
    )
    scheduled_workouts = session.exec(scheduled_workouts_stmt).one()
    
    # Total duration
    total_duration_stmt = (
        select(func.sum(Workout.duration_minutes))
        .where(Workout.user_id == current_user.id)
        .where(Workout.duration_minutes != None)
    )
    total_duration = session.exec(total_duration_stmt).one() or 0
    
    # Average duration
    avg_duration_stmt = (
        select(func.avg(Workout.duration_minutes))
        .where(Workout.user_id == current_user.id)
        .where(Workout.duration_minutes != None)
    )
    avg_duration = session.exec(avg_duration_stmt).one() or 0
    
    return {
        "total_workouts": total_workouts,
        "completed_workouts": completed_workouts,
        "scheduled_workouts": scheduled_workouts,
        "total_duration_minutes": total_duration,
        "average_duration_minutes": round(avg_duration, 1),
    }


@router.post("/{workout_id}/exercises", response_model=ExercisePublic)
def add_exercise(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    workout_id: uuid.UUID = Path(..., description="The ID of the workout to add the exercise to"),
    exercise_in: ExerciseCreate = Body(
        ...,
        examples=[
            {
                "name": "Bench Press",
                "description": "Flat bench press with barbell",
                "category": "Strength",
                "sets": 4,
                "reps": 8,
                "weight": 135.5
            }
        ],
    )
) -> Any:
    """
    Add an exercise to a workout.
    
    This endpoint allows users to add an exercise to an existing workout.
    
    - **workout_id**: The UUID of the workout to add the exercise to
    - **name**: Required. The name of the exercise (1-255 characters)
    - **description**: Optional. A detailed description of the exercise (up to 1000 characters)
    - **category**: Required. The category of the exercise (e.g., Strength, Cardio)
    - **sets**: Optional. The number of sets
    - **reps**: Optional. The number of repetitions per set
    - **weight**: Optional. The weight used (in pounds/kg)
    
    Returns the created exercise.
    
    Raises:
    - 404: If the workout is not found
    - 403: If the workout doesn't belong to the current user
    """
    # Check if workout exists and belongs to user
    workout = session.get(Workout, workout_id)
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Create exercise
    exercise = Exercise(
        workout_id=workout_id,
        name=exercise_in.name,
        description=exercise_in.description,
        category=exercise_in.category,
        sets=exercise_in.sets,
        reps=exercise_in.reps,
        weight=exercise_in.weight,
        created_at=datetime.utcnow(),
    )
    
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    
    return exercise


@router.get("/{workout_id}/exercises", response_model=List[ExercisePublic])
def get_exercises(
    workout_id: uuid.UUID = Path(..., description="The ID of the workout to get exercises for"),
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Get exercises for a workout.
    
    This endpoint retrieves all exercises associated with a specific workout.
    
    - **workout_id**: The UUID of the workout to get exercises for
    
    Returns a list of exercises.
    
    Raises:
    - 404: If the workout is not found
    - 403: If the workout doesn't belong to the current user
    """
    # Check if workout exists and belongs to user
    workout = session.get(Workout, workout_id)
    
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get exercises
    statement = select(Exercise).where(Exercise.workout_id == workout_id)
    exercises = session.exec(statement).all()
    
    return exercises


@router.put("/exercises/{exercise_id}", response_model=ExercisePublic)
def update_exercise(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    exercise_id: uuid.UUID = Path(..., description="The ID of the exercise to update"),
    exercise_in: ExerciseUpdate = Body(
        ...,
        examples=[
            {
                "name": "Incline Bench Press",
                "description": "Incline bench press with dumbbells",
                "category": "Strength",
                "sets": 3,
                "reps": 10,
                "weight": 50.0
            }
        ],
    )
) -> Any:
    """
    Update an exercise.
    
    This endpoint allows users to update an existing exercise's details.
    
    - **exercise_id**: The UUID of the exercise to update
    - **name**: Optional. The updated name of the exercise
    - **description**: Optional. The updated description
    - **category**: Optional. The updated category
    - **sets**: Optional. The updated number of sets
    - **reps**: Optional. The updated number of repetitions
    - **weight**: Optional. The updated weight
    
    Returns the updated exercise.
    
    Raises:
    - 404: If the exercise is not found
    - 403: If the exercise's workout doesn't belong to the current user
    """
    # Get exercise
    exercise = session.get(Exercise, exercise_id)
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    # Check if workout belongs to user
    workout = session.get(Workout, exercise.workout_id)
    
    if not workout or workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update exercise
    update_dict = exercise_in.model_dump(exclude_unset=True)
    
    # Set updated_at timestamp
    update_dict["updated_at"] = datetime.utcnow()
    
    exercise.sqlmodel_update(update_dict)
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    
    return exercise


@router.delete("/exercises/{exercise_id}", response_model=Message)
def delete_exercise(
    exercise_id: uuid.UUID = Path(..., description="The ID of the exercise to delete"),
    session: SessionDep = None,
    current_user: CurrentUser = None,
) -> Any:
    """
    Delete an exercise.
    
    This endpoint allows users to delete an exercise from a workout.
    
    - **exercise_id**: The UUID of the exercise to delete
    
    Returns a success message.
    
    Raises:
    - 404: If the exercise is not found
    - 403: If the exercise's workout doesn't belong to the current user
    """
    # Get exercise
    exercise = session.get(Exercise, exercise_id)
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    # Check if workout belongs to user
    workout = session.get(Workout, exercise.workout_id)
    
    if not workout or workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Delete exercise
    session.delete(exercise)
    session.commit()
    
    return Message(message="Exercise deleted successfully")


@router.get("/exercises/library", response_model=List[dict])
def get_exercise_library() -> Any:
    """
    Get exercise library.
    
    This endpoint provides a library of common exercises that users can add to their workouts.
    The library is organized by category and includes exercise names and descriptions.
    
    Returns a list of exercise categories, each containing a list of exercises.
    """
    # This is a static library of common exercises
    return [
        {
            "category": "Strength",
            "exercises": [
                {
                    "name": "Bench Press",
                    "description": "Lie on a flat bench and press a barbell upwards",
                    "muscle_groups": ["Chest", "Shoulders", "Triceps"]
                },
                {
                    "name": "Squat",
                    "description": "Lower your body by bending your knees and hips, then return to standing",
                    "muscle_groups": ["Quadriceps", "Hamstrings", "Glutes"]
                },
                {
                    "name": "Deadlift",
                    "description": "Lift a barbell from the ground to hip level",
                    "muscle_groups": ["Back", "Hamstrings", "Glutes"]
                },
                {
                    "name": "Overhead Press",
                    "description": "Press a barbell or dumbbells overhead from shoulder height",
                    "muscle_groups": ["Shoulders", "Triceps"]
                },
                {
                    "name": "Pull-up",
                    "description": "Pull your body up to a bar from a hanging position",
                    "muscle_groups": ["Back", "Biceps"]
                }
            ]
        },
        {
            "category": "Cardio",
            "exercises": [
                {
                    "name": "Running",
                    "description": "Running at a steady pace",
                    "muscle_groups": ["Legs", "Core"]
                },
                {
                    "name": "Cycling",
                    "description": "Cycling on a stationary bike or outdoors",
                    "muscle_groups": ["Legs"]
                },
                {
                    "name": "Rowing",
                    "description": "Using a rowing machine for full-body cardio",
                    "muscle_groups": ["Back", "Arms", "Legs"]
                },
                {
                    "name": "Jump Rope",
                    "description": "Skipping with a jump rope",
                    "muscle_groups": ["Legs", "Shoulders"]
                },
                {
                    "name": "HIIT",
                    "description": "High-intensity interval training with alternating work and rest periods",
                    "muscle_groups": ["Full Body"]
                }
            ]
        },
        {
            "category": "Flexibility",
            "exercises": [
                {
                    "name": "Yoga",
                    "description": "Various yoga poses and flows",
                    "muscle_groups": ["Full Body"]
                },
                {
                    "name": "Static Stretching",
                    "description": "Holding stretches for extended periods",
                    "muscle_groups": ["Full Body"]
                },
                {
                    "name": "Dynamic Stretching",
                    "description": "Moving stretches that prepare the body for exercise",
                    "muscle_groups": ["Full Body"]
                }
            ]
        }
    ]