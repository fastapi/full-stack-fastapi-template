from datetime import date
from sqlmodel import Session

from app.models import Workout, PersonalBestCreate
from app.crud.pbests import create_or_update_personal_best, TRACKED_EXERCISES

def update_personal_bests_after_workout(*, session: Session, workout: Workout):
    user_id = workout.user_id

    # Fetch all exercises associated with this workout
    exercises = workout.exercises

    for exercise in exercises:
        name = exercise.name.lower()
        metric_key = TRACKED_EXERCISES.get(name)
        if not metric_key:
            #
            continue  # skip exercises we don't track

        # Use weight * reps as performance metric for now
        value = (exercise.weight or 0) * (exercise.reps or 0)
        if value <= 0:
            #continue
            value = 0

        pb_in = PersonalBestCreate(metric=metric_key, value=value, date=date.today())

        from app.crud import create_or_update_personal_best  # to avoid circular imports
        create_or_update_personal_best(session=session, user_id=user_id, pb_in=pb_in)