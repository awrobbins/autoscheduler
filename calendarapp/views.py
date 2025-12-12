from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass
from typing import Optional

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


@dataclass(frozen=True)
class DayCell:
    """
    Represents one cell in the calendar grid.
    If day == 0, it's a padding cell (outside the current month).
    """
    day: int
    date: Optional[dt.date]


def _parse_year_month(request: HttpRequest) -> tuple[int, int]:
    """
    Read ?year=YYYY&month=MM from the URL.
    If missing/invalid, default to today's year/month.
    """
    today = dt.date.today()

    try:
        year = int(request.GET.get("year", today.year))
        month = int(request.GET.get("month", today.month))
        if month < 1 or month > 12:
            raise ValueError("month out of range")
    except (TypeError, ValueError):
        year, month = today.year, today.month

    return year, month


def _build_month_grid(year: int, month: int) -> list[list[DayCell]]:
    """
    Build a 2D grid (weeks x days) of DayCell objects.
    Uses Sunday as the first day of the week.
    """
    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    weeks: list[list[DayCell]] = []

    for week in cal.monthdayscalendar(year, month):
        row: list[DayCell] = []
        for day_num in week:
            if day_num == 0:
                row.append(DayCell(day=0, date=None))
            else:
                row.append(DayCell(day=day_num, date=dt.date(year, month, day_num)))
        weeks.append(row)

    return weeks


def month_view(request: HttpRequest) -> HttpResponse:
    year, month = _parse_year_month(request)
    month_name = dt.date(year, month, 1).strftime("%B")

    # For simple prev/next navigation
    first = dt.date(year, month, 1)
    prev_month = (first - dt.timedelta(days=1)).replace(day=1)
    next_month = (first.replace(day=28) + dt.timedelta(days=4)).replace(day=1)

    context = {
        "year": year,
        "month": month,
        "month_name": month_name,
        "weeks": _build_month_grid(year, month),
        "prev_year": prev_month.year,
        "prev_month": prev_month.month,
        "next_year": next_month.year,
        "next_month": next_month.month,
        "today": dt.date.today(),
    }
    return render(request, "calendarapp/month.html", context)

