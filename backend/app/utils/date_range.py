from datetime import timedelta,date
from typing import Tuple, List as TypingList


def get_week_boundaries(date_val: date) -> Tuple[date, date]:
    """Get start (Monday) and end (Sunday) of the week for a given date"""
    start = date_val - timedelta(days=date_val.weekday())
    end = start + timedelta(days=6)
    return start, end


def get_month_boundaries(date_val: date) -> Tuple[date, date]:
    """Get first and last day of the month"""
    start = date_val.replace(day=1)
    if date_val.month == 12:
        end = date_val.replace(day=31)
    else:
        end = (start.replace(month=start.month + 1) - timedelta(days=1))
    return start, end


def get_quarter_boundaries(date_val: date) -> Tuple[date, date]:
    """Get first and last day of the quarter"""
    quarter = (date_val.month - 1) // 3 + 1
    start_month = (quarter - 1) * 3 + 1
    start = date_val.replace(month=start_month, day=1)

    if quarter == 4:
        end = date_val.replace(month=12, day=31)
    else:
        end_month = start_month + 2
        if end_month == 12:
            end = date_val.replace(month=12, day=31)
        else:
            end = (date_val.replace(month=end_month + 1, day=1) - timedelta(days=1))
    return start, end


def get_year_boundaries(date_val: date) -> Tuple[date, date]:
    """Get first and last day of the year"""
    start = date_val.replace(month=1, day=1)
    end = date_val.replace(month=12, day=31)
    return start, end


def generate_periods(start_date: date, end_date: date, aggregation: str) -> TypingList[Tuple[date, date]]:
    """Generate list of period boundaries based on aggregation level"""
    periods = []
    current = start_date

    boundary_func = {
        'week': get_week_boundaries,
        'month': get_month_boundaries,
        'quarter': get_quarter_boundaries,
        'year': get_year_boundaries
    }[aggregation]

    while current <= end_date:
        period_start, period_end = boundary_func(current)

        # Adjust to actual query range
        actual_start = max(period_start, start_date)
        actual_end = min(period_end, end_date)

        if actual_start <= actual_end:
            periods.append((actual_start, actual_end))

        # Move to next period
        if aggregation == 'week':
            current = period_end + timedelta(days=1)
        elif aggregation == 'month':
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        elif aggregation == 'quarter':
            if current.month >= 10:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 3)
        else:  # year
            current = current.replace(year=current.year + 1)

    return periods
