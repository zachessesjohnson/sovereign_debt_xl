from __future__ import annotations

from typing import Any


from ._coerce import safe_err, to_1d_floats, to_2d_list


def amortization_profile(bonds_list: Any) -> list[list[Any]] | str:
    """Build a redemption wall from a list of [maturity_year, face_value] bond rows.

    An optional header row (detected when the first cell is a string) is skipped.
    A concentration flag of "HIGH" is set for any year whose redemption represents
    25 % or more of the total outstanding amount.
    """
    try:
        grid = to_2d_list(bonds_list)
        if not grid:
            return safe_err(ValueError("bonds_list is empty"))
        start = 1 if isinstance(grid[0][0], str) else 0
        profile: dict[int, float] = {}
        for row in grid[start:]:
            if len(row) < 2:
                continue
            try:
                yr = int(float(row[0]))
                fv = float(row[1])
            except Exception:
                continue
            profile[yr] = profile.get(yr, 0.0) + fv
        if not profile:
            return safe_err(ValueError("No valid bond rows found"))
        total = sum(profile.values())
        out: list[list[Any]] = [["year", "redemption", "concentration_flag"]]
        for yr in sorted(profile.keys()):
            redemption = profile[yr]
            flag = "HIGH" if redemption > 0.25 * total else ""
            out.append([yr, round(redemption, 4), flag])
        return out
    except Exception as e:
        return safe_err(e)


def weighted_avg_maturity(bonds_outstanding: Any) -> float | str:
    """Weighted average maturity of a debt portfolio.

    bonds_outstanding: list of [maturity_years, face_value] rows.
    An optional header row is skipped when the first cell is a string.
    """
    try:
        grid = to_2d_list(bonds_outstanding)
        if not grid:
            return safe_err(ValueError("bonds_outstanding is empty"))
        start = 1 if isinstance(grid[0][0], str) else 0
        wam_sum = 0.0
        total_value = 0.0
        for row in grid[start:]:
            if len(row) < 2:
                continue
            try:
                mat = float(row[0])
                fv = float(row[1])
            except Exception:
                continue
            wam_sum += mat * fv
            total_value += fv
        if total_value == 0:
            return safe_err(ValueError("Total face value is zero"))
        return round(wam_sum / total_value, 4)
    except Exception as e:
        return safe_err(e)


def gross_financing_need(
    amortization_schedule: Any,
    projected_deficit: float,
    year: int,
) -> float | str:
    """Gross financing need for a given year.

    GFN = amortization due in that year + projected fiscal deficit.
    year is 1-based (1 = first element of amortization_schedule).
    """
    try:
        sched = to_1d_floats(amortization_schedule)
        if not sched:
            return safe_err(ValueError("amortization_schedule is empty"))
        if year < 1 or year > len(sched):
            return safe_err(ValueError(f"year must be between 1 and {len(sched)}"))
        return round(sched[year - 1] + float(projected_deficit), 6)
    except Exception as e:
        return safe_err(e)
