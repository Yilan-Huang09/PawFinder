from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.services.matching import (
    calculate_distance_score,
    calculate_time_score,
    haversine_km,
)


@pytest.mark.parametrize(
    ("distance_km", "expected"),
    [
        (0.2, 100.0),
        (1.5, 90.0),
        (4.0, 75.0),
        (8.0, 55.0),
        (15.0, 30.0),
        (35.0, 10.0),
        (51.0, 0.0),
    ],
)
def test_distance_score_boundaries(distance_km, expected):
    assert calculate_distance_score(distance_km) == expected


@pytest.mark.parametrize(
    ("hours", "expected"),
    [
        (2, 100.0),
        (12, 90.0),
        (48, 75.0),
        (120, 60.0),
        (300, 35.0),
        (800, 10.0),
    ],
)
def test_time_score_boundaries(hours, expected):
    lost_time = datetime(2026, 11, 1, 8, 0, 0)
    assert calculate_time_score(lost_time, lost_time + timedelta(hours=hours)) == expected


def test_haversine_distance_is_symmetric_and_zero_for_same_point():
    assert haversine_km(30.2741, 120.1551, 30.2741, 120.1551) == 0.0
    forward = haversine_km(30.2741, 120.1551, 30.2841, 120.1651)
    backward = haversine_km(30.2841, 120.1651, 30.2741, 120.1551)
    assert forward == pytest.approx(backward, abs=0.001)
    assert forward == pytest.approx(1.47, abs=0.05)
