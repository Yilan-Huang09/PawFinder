from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime

from ..extensions import db
from ..models.lost_case import LostCase
from ..models.match import CaseSightingMatch
from ..models.sighting import Sighting


ALGORITHM_VERSION = "rule-v1"
MIN_PERSISTED_SCORE = 40.0
MAX_CANDIDATE_DISTANCE_KM = 50.0
FEATURE_TERMS = (
    "项圈",
    "胸口",
    "胸背",
    "耳朵",
    "耳尖",
    "缺口",
    "尾巴",
    "眼睛",
    "鼻梁",
    "铃铛",
    "前爪",
    "后腿",
)


@dataclass(frozen=True)
class MatchResult:
    appearance_score: float
    distance_score: float
    time_score: float
    total_score: float
    distance_km: float
    reason: str


def _normalized(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).upper()


def haversine_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    radius_km = 6371.0088
    lat1 = math.radians(latitude_1)
    lat2 = math.radians(latitude_2)
    delta_lat = math.radians(latitude_2 - latitude_1)
    delta_lon = math.radians(longitude_2 - longitude_1)
    value = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    value = min(1.0, max(0.0, value))
    return round(radius_km * 2 * math.asin(math.sqrt(value)), 3)


def calculate_distance_score(distance_km: float) -> float:
    if distance_km <= 0.5:
        return 100.0
    if distance_km <= 2:
        return 90.0
    if distance_km <= 5:
        return 75.0
    if distance_km <= 10:
        return 55.0
    if distance_km <= 20:
        return 30.0
    if distance_km <= 50:
        return 10.0
    return 0.0


def calculate_time_score(lost_time: datetime, seen_time: datetime) -> float:
    hours = (seen_time - lost_time).total_seconds() / 3600
    if hours < 0:
        return 0.0
    if hours <= 6:
        return 100.0
    if hours <= 24:
        return 90.0
    if hours <= 72:
        return 75.0
    if hours <= 168:
        return 60.0
    if hours <= 720:
        return 35.0
    return 10.0


def calculate_appearance_score(lost_case: LostCase, sighting: Sighting) -> tuple[float, list[str]]:
    pet = lost_case.pet
    score = 0.0
    reasons: list[str] = []

    pet_breed = _normalized(pet.breed)
    sighting_breed = _normalized(sighting.breed_guess)
    if pet_breed and sighting_breed and pet_breed == sighting_breed:
        score += 25
        reasons.append("品种吻合")
    elif not pet_breed or not sighting_breed:
        score += 10
        reasons.append("品种信息不完整")

    pet_primary = _normalized(pet.primary_color)
    pet_secondary = _normalized(pet.secondary_color)
    sighting_primary = _normalized(sighting.primary_color)
    sighting_secondary = _normalized(sighting.secondary_color)
    pet_colors = {color for color in (pet_primary, pet_secondary) if color}
    sighting_colors = {color for color in (sighting_primary, sighting_secondary) if color}
    if pet_primary == sighting_primary:
        score += 25
        reasons.append("主要毛色吻合")
    elif pet_primary in sighting_colors:
        score += 12.5
        reasons.append("主要毛色部分吻合")
    color_overlap = pet_colors & sighting_colors
    if len(color_overlap) >= 2:
        score += 10
        reasons.append("次要毛色吻合")
    elif color_overlap:
        score += 5

    if pet.gender == sighting.gender_guess:
        score += 15
        reasons.append("性别吻合")
    elif "UNKNOWN" in {pet.gender, sighting.gender_guess}:
        score += 7.5

    if pet.size == sighting.size_guess:
        score += 15
        reasons.append("体型吻合")
    elif "UNKNOWN" in {pet.size, sighting.size_guess}:
        score += 7.5

    pet_text = _normalized(pet.distinctive_features)
    sighting_text = _normalized(sighting.description)
    pet_terms = {term for term in FEATURE_TERMS if term in pet_text}
    sighting_terms = {term for term in FEATURE_TERMS if term in sighting_text}
    if pet_terms:
        overlap_ratio = len(pet_terms & sighting_terms) / len(pet_terms)
        feature_score = round(20 * overlap_ratio, 2)
        score += feature_score
        if feature_score:
            reasons.append(f"显著特征吻合 {feature_score:.0f}/20")
    else:
        score += 10
        reasons.append("缺少可比较的显著特征")

    return round(min(100.0, score), 2), reasons


def score_pair(lost_case: LostCase, sighting: Sighting) -> MatchResult | None:
    if lost_case.status != "SEARCHING" or sighting.status != "ACTIVE":
        return None
    if _normalized(lost_case.pet.species) != _normalized(sighting.species):
        return None
    if sighting.seen_time < lost_case.lost_time:
        return None

    distance_km = haversine_km(
        float(lost_case.latitude),
        float(lost_case.longitude),
        float(sighting.latitude),
        float(sighting.longitude),
    )
    if distance_km > MAX_CANDIDATE_DISTANCE_KM:
        return None

    appearance_score, appearance_reasons = calculate_appearance_score(lost_case, sighting)
    distance_score = calculate_distance_score(distance_km)
    time_score = calculate_time_score(lost_case.lost_time, sighting.seen_time)
    total_score = round(
        appearance_score * 0.50 + distance_score * 0.30 + time_score * 0.20,
        2,
    )
    hours = (sighting.seen_time - lost_case.lost_time).total_seconds() / 3600
    reason = (
        f"外观 {appearance_score:.1f} 分（{'、'.join(appearance_reasons) or '无明显吻合项'}）；"
        f"距离 {distance_km:.3f} km，{distance_score:.1f} 分；"
        f"时间间隔 {hours:.1f} 小时，{time_score:.1f} 分。"
    )
    return MatchResult(
        appearance_score=appearance_score,
        distance_score=distance_score,
        time_score=time_score,
        total_score=total_score,
        distance_km=distance_km,
        reason=reason,
    )


def _persist_result(
    lost_case: LostCase,
    sighting: Sighting,
    result: MatchResult | None,
) -> CaseSightingMatch | None:
    existing = CaseSightingMatch.query.filter_by(
        case_id=lost_case.case_id,
        sighting_id=sighting.sighting_id,
    ).first()
    if result is None or result.total_score < MIN_PERSISTED_SCORE:
        if existing is not None and existing.review_status == "PENDING":
            db.session.delete(existing)
        return None

    match = existing or CaseSightingMatch(
        case_id=lost_case.case_id,
        sighting_id=sighting.sighting_id,
        review_status="PENDING",
    )
    match.appearance_score = result.appearance_score
    match.distance_score = result.distance_score
    match.time_score = result.time_score
    match.total_score = result.total_score
    match.distance_km = result.distance_km
    match.match_reason = result.reason
    match.algorithm_version = ALGORITHM_VERSION
    if existing is None:
        db.session.add(match)
    return match


def recalculate_for_case(case_id: int) -> list[int]:
    lost_case = db.session.get(LostCase, case_id)
    if lost_case is None or lost_case.status != "SEARCHING":
        return []
    candidates = Sighting.query.filter(
        Sighting.status == "ACTIVE",
        Sighting.species == lost_case.pet.species,
        Sighting.seen_time >= lost_case.lost_time,
    ).all()
    persisted: list[CaseSightingMatch] = []
    candidate_ids = {sighting.sighting_id for sighting in candidates}
    for sighting in candidates:
        match = _persist_result(lost_case, sighting, score_pair(lost_case, sighting))
        if match is not None:
            persisted.append(match)

    stale = CaseSightingMatch.query.filter_by(case_id=case_id, review_status="PENDING").all()
    for match in stale:
        if match.sighting_id not in candidate_ids:
            db.session.delete(match)
    db.session.commit()
    return [match.match_id for match in persisted]


def recalculate_for_sighting(sighting_id: int) -> list[int]:
    sighting = db.session.get(Sighting, sighting_id)
    if sighting is None or sighting.status != "ACTIVE":
        return []
    cases = LostCase.query.filter(
        LostCase.status == "SEARCHING",
        LostCase.lost_time <= sighting.seen_time,
    ).all()
    cases = [case for case in cases if _normalized(case.pet.species) == _normalized(sighting.species)]
    persisted: list[CaseSightingMatch] = []
    case_ids = {lost_case.case_id for lost_case in cases}
    for lost_case in cases:
        match = _persist_result(lost_case, sighting, score_pair(lost_case, sighting))
        if match is not None:
            persisted.append(match)
    stale = CaseSightingMatch.query.filter_by(
        sighting_id=sighting_id,
        review_status="PENDING",
    ).all()
    for match in stale:
        if match.case_id not in case_ids:
            db.session.delete(match)
    db.session.commit()
    return [match.match_id for match in persisted]
