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
    WorkoutsPublic,
    WorkoutWithExercisesPublic,
    WorkoutExercise,
    WorkoutExerciseCreate,
    WorkoutExerciseUpdate,
    WorkoutExercisePublic,
    WorkoutSet,
    WorkoutSetCreate,
    WorkoutSetUpdate,
    WorkoutSetPublic,
)
from app.crud.workouts import update_personal_bests_after_workout


router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/", response_model=WorkoutWithExercisesPublic)
def create_workout(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    workout_in: WorkoutCreate
):
    workout = Workout(
        user_id=current_user.id,
        name=workout_in.name,
        description=workout_in.description,
        scheduled_date=workout_in.scheduled_date,
        duration_minutes=workout_in.duration_minutes,
        is_completed=workout_in.is_completed or False,
        completed_date=workout_in.completed_date,
        created_at=datetime.utcnow(),
    )

    session.add(workout)
    session.flush()  # Get workout.id

    for ex in workout_in.exercises:
        w_ex = WorkoutExercise(
            workout_id=workout.id,
            name=ex.name,
            muscle_group=ex.muscle_group,
            type=ex.type,
            created_at=datetime.utcnow(),
        )
        session.add(w_ex)
        session.flush()  # Get w_ex.id

        for s in ex.sets:
            set_obj = WorkoutSet(
                exercise_id=w_ex.id,
                weight=s.weight,
                reps=s.reps
            )
            session.add(set_obj)

    session.commit()
    session.refresh(workout)
    return workout




@router.get("/", response_model=WorkoutsPublic)
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
    
    return WorkoutsPublic(data=workouts, count=count)


@router.get("/{workout_id}", response_model=WorkoutWithExercisesPublic)
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


@router.get("/scheduled", response_model=WorkoutsPublic)
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
    
    return WorkoutsPublic(data=workouts, count=count)


@router.get("/completed", response_model=WorkoutsPublic)
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
    
    return WorkoutsPublic(data=workouts, count=count)


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


@router.post("/{workout_id}/exercises", response_model=WorkoutExercisePublic)
def add_exercise(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    workout_id: uuid.UUID,
    exercise_in: WorkoutExerciseCreate
) -> Any:
    workout = session.get(Workout, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    if workout.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    workout_ex = WorkoutExercise(
        workout_id=workout_id,
        name=exercise_in.name,
        muscle_group=exercise_in.muscle_group,
        type=exercise_in.type,
        created_at=datetime.utcnow()
    )
    session.add(workout_ex)
    session.flush()  # to get ID

    for set_in in exercise_in.sets:
        w_set = WorkoutSet(
            exercise_id=workout_ex.id,
            weight=set_in.weight,
            reps=set_in.reps
        )
        session.add(w_set)

    session.commit()
    session.refresh(workout_ex)

    # Manually load sets for response
    workout_ex.sets = session.exec(
        select(WorkoutSet).where(WorkoutSet.exercise_id == workout_ex.id)
    ).all()

    return workout_ex



@router.get("/{workout_id}/exercises", response_model=List[WorkoutExercisePublic])
def get_exercises(
    workout_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    workout = session.get(Workout, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    if workout.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    exercises = session.exec(
        select(WorkoutExercise).where(WorkoutExercise.workout_id == workout_id)
    ).all()

    for ex in exercises:
        ex.sets = session.exec(
            select(WorkoutSet).where(WorkoutSet.exercise_id == ex.id)
        ).all()

    return exercises



@router.put("/exercises/{exercise_id}", response_model=WorkoutExercisePublic)
def update_exercise(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    exercise_id: uuid.UUID,
    exercise_in: WorkoutExerciseUpdate
) -> Any:
    exercise = session.get(WorkoutExercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    workout = session.get(Workout, exercise.workout_id)
    if not workout or workout.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = exercise_in.model_dump(exclude_unset=True, exclude={"sets"})
    for key, value in update_data.items():
        setattr(exercise, key, value)
    session.add(exercise)

    # Replace sets if provided
    if exercise_in.sets is not None:
        session.exec(
            select(WorkoutSet)
            .where(WorkoutSet.exercise_id == exercise.id)
        ).all()
        session.exec(
            select(WorkoutSet)
            .where(WorkoutSet.exercise_id == exercise.id)
        ).delete()
        for s in exercise_in.sets:
            session.add(
                WorkoutSet(
                    exercise_id=exercise.id,
                    weight=s.weight,
                    reps=s.reps
                )
            )

    session.commit()
    session.refresh(exercise)

    # Reload sets
    exercise.sets = session.exec(
        select(WorkoutSet).where(WorkoutSet.exercise_id == exercise.id)
    ).all()

    return exercise



@router.delete("/exercises/{exercise_id}", response_model=Message)
def delete_exercise(
    exercise_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    exercise = session.get(WorkoutExercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    workout = session.get(Workout, exercise.workout_id)
    if not workout or workout.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

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