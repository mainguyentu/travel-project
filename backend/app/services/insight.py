from __future__ import annotations

import math
import re
import statistics
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import DestinationInsight

BASELINE_SCORE = 50.0

DIMENSIONS = ("scenery", "accessibility", "crowd", "value")

KEYWORDS: dict[str, list[str]] = {
    "scenery": [
        "đẹp",
        "view",
        "phong cảnh",
        "cảnh quan",
        "chill",
        "biển",
        "núi",
        "thiên nhiên",
        "hùng vĩ",
        "hoang sơ",
        "check-in",
        "sống ảo",
        "instagram",
    ],
    "accessibility": [
        "dễ đi",
        "khó đi",
        "xa",
        "gần trung tâm",
        "đường",
        "đường xấu",
        "đèo dốc",
        "xe",
        "grab",
        "taxi",
        "di chuyển",
        "phượt",
        "xe máy",
        "đi bộ",
    ],
    "crowd": [
        "đông",
        "vắng",
        "chen",
        "chen chúc",
        "quá tải",
        "ít người",
        "vắng vẻ",
        "peak season",
        "cuối tuần đông",
        "đông vui",
        "đông chán",
    ],
    "value": [
        "giá",
        "đắt",
        "rẻ",
        "phí",
        "dịch vụ",
        "xứng đáng",
        "đáng tiền",
        "ăn uống đắt",
        "phí vào cửa",
        "tiền nào của nấy",
        "chất lượng dịch vụ",
    ],
}

POSITIVE_WORDS = {
    "đẹp",
    "tốt",
    "ổn",
    "rẻ",
    "hợp lý",
    "thuận tiện",
    "dễ",
    "đáng",
    "tuyệt",
    "xuất sắc",
    "xứng đáng",
    "thích",
}
NEGATIVE_WORDS = {
    "đông",
    "đắt",
    "khó",
    "tệ",
    "xa",
    "chật",
    "ồn",
    "bẩn",
    "nguy hiểm",
    "thất vọng",
}

PHRASE_SENTIMENTS: dict[str, float] = {
    "đông vui": 0.5,
    "nhộn nhịp": 0.5,
    "quá đông": -1.5,
    "chen chúc": -2.0,
    "quá tải": -2.0,
    "vắng vẻ": 1.0,
    "yên tĩnh": 1.0,
    "không quá đẹp": -0.5,
    "không đẹp": -1.0,
    "không đáng": -1.0,
}
NEGATION_WORDS = {"không", "chưa", "ít", "chẳng"}

INTENSIFIERS_POSITIVE: dict[str, float] = {"rất": 1.5, "cực kỳ": 1.7, "siêu": 2.0, "tuyệt vời": 2.0}
INTENSIFIERS_NEGATIVE: dict[str, float] = {"rất": 1.5, "cực kỳ": 1.7, "quá": 1.7}

AD_PHRASES = ["liên hệ", "zalo", "telegram", "facebook", "fb"]
UNRELATED_PHRASES = [
    "ship nhanh",
    "shop uy tín",
    "giao nhanh",
    "mua hàng",
    "đặt hàng",
    "order",
    "khuyến mãi",
    "sale",
]

MEANINGLESS_WORDS = {"ok", "good", "kkkk", "kkk", "haha", "hehe"}

REPEAT_CHAR_RE = re.compile(r"(.)\1{4,}", re.IGNORECASE)
REPEAT_WORD_RE = re.compile(r"\b(\w+)(?:\s+\1){2,}\b", re.IGNORECASE)
ONLY_SYMBOL_RE = re.compile(r"^[\W_]+$", re.UNICODE)
URL_RE = re.compile(r"(https?://|www\.)\S+", re.IGNORECASE)
PHONE_RE = re.compile(r"\b0\d{8,10}\b|\b\d{9,12}\b")
DOTS_RE = re.compile(r"^[\.\s]+$")
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF]",
    flags=re.UNICODE,
)

CACHE_VERSION = 2

# Time-decay: mục tiêu ~0.8 sau ~24 tháng (gần hướng dẫn trong design).
DECAY_TARGET_AT_24_MONTHS = 0.8
DECAY_DAYS_24_MONTHS = 730.0
DECAY_LAMBDA_PER_DAY = -math.log(DECAY_TARGET_AT_24_MONTHS) / DECAY_DAYS_24_MONTHS
MIN_TIME_DECAY = 0.6


def _clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in text.split():
        token = re.sub(r"[^\wÀ-ỹ]+", "", raw, flags=re.UNICODE)
        if token:
            tokens.append(token)
    return tokens


def _has_negation_before(tokens: list[str], index: int, window: int = 2) -> bool:
    start = max(0, index - window)
    return any(tokens[i] in NEGATION_WORDS for i in range(start, index))


def _score_token_sentiment(token: str) -> float:
    if token in POSITIVE_WORDS:
        return 1.0
    if token in NEGATIVE_WORDS:
        return -1.0
    return 0.0



def _phrase_sentiment_bonus(text: str) -> float:
    score = 0.0
    for phrase, value in PHRASE_SENTIMENTS.items():
        if phrase in text:
            score += value
    return score


def _detect_sentiment_weight(text: str, tokens: list[str]) -> float:
    if not tokens:
        return 0.3

    split_idx = None
    for idx, token in enumerate(tokens):
        if token in {"nhưng", "nhung", "but", "however"}:
            split_idx = idx
            break

    def _compute_segment(segment_tokens: list[str], segment_text: str, segment_weight: float) -> float:
        raw_score = 0.0
        for i, token in enumerate(segment_tokens):
            token_score = _score_token_sentiment(token)
            if token_score == 0.0:
                continue
            if _has_negation_before(segment_tokens, i):
                token_score *= -1.0

            prev_token = segment_tokens[i - 1] if i - 1 >= 0 else ""
            prev_prev = segment_tokens[i - 2] if i - 2 >= 0 else ""
            phrase = f"{prev_prev} {prev_token}".strip()

            if token_score > 0 and prev_token in INTENSIFIERS_POSITIVE:
                token_score *= float(INTENSIFIERS_POSITIVE[prev_token])
            elif token_score < 0 and prev_token in INTENSIFIERS_NEGATIVE:
                token_score *= float(INTENSIFIERS_NEGATIVE[prev_token])
            elif token_score > 0 and phrase in INTENSIFIERS_POSITIVE:
                token_score *= float(INTENSIFIERS_POSITIVE[phrase])
            elif token_score < 0 and phrase in INTENSIFIERS_NEGATIVE:
                token_score *= float(INTENSIFIERS_NEGATIVE[phrase])

            raw_score += token_score

        if "tuyệt vời" in segment_text and raw_score > 0:
            raw_score = max(raw_score, 3.0)
        if "quá tệ" in segment_text and raw_score < 0:
            raw_score = min(raw_score, -3.0)

        return raw_score * segment_weight

    if split_idx is None:
        score = _compute_segment(tokens, text, 1.0)
    else:
        before = tokens[:split_idx]
        after = tokens[split_idx + 1 :]
        score = _compute_segment(before, " ".join(before), 1.0) + _compute_segment(after, " ".join(after), 1.5)

    score += _phrase_sentiment_bonus(text)

    if score >= 2.5:
        return 15.0
    if score >= 1.5:
        return 10.0
    if score >= 0.5:
        return 5.0
    if score <= -2.5:
        return -15.0
    if score <= -1.5:
        return -10.0
    if score <= -0.5:
        return -5.0
    return 0.0


def _latin_ratio(text: str) -> float:
    total_alpha = 0
    latin_alpha = 0
    for ch in text:
        if ch.isalpha():
            total_alpha += 1
            if re.match(r"[A-Za-zÀ-ỹ]", ch):
                latin_alpha += 1
    if total_alpha == 0:
        return 0.0
    return latin_alpha / total_alpha


def _is_spam_language(text: str) -> bool:
    return _latin_ratio(text) < 0.7


def _repeat_word_spam(tokens: list[str]) -> bool:
    if len(tokens) < 3:
        return False
    if REPEAT_WORD_RE.search(" ".join(tokens)):
        return True
    top_freq = max(tokens.count(token) for token in set(tokens))
    return top_freq / len(tokens) >= 0.6


def _spam_multiplier(text: str, tokens: list[str], has_keyword: bool) -> float | None:
    if not text:
        return None
    normalized = text

    stripped_emojis = EMOJI_RE.sub("", normalized).strip()
    if not stripped_emojis:
        return None

    if DOTS_RE.match(normalized) or ONLY_SYMBOL_RE.match(normalized):
        return 0.3 if has_keyword else None
    if any(token in MEANINGLESS_WORDS for token in tokens):
        return 0.3 if has_keyword else None
    if len(tokens) < 5:
        return 0.3 if has_keyword else None
    if REPEAT_CHAR_RE.search(normalized) or _repeat_word_spam(tokens):
        return 0.3 if has_keyword else None

    if URL_RE.search(normalized) or PHONE_RE.search(normalized):
        return None
    if any(phrase in normalized for phrase in AD_PHRASES):
        return None
    if any(phrase in normalized for phrase in UNRELATED_PHRASES):
        return None
    if _is_spam_language(normalized):
        return None

    return 1.0


def _parse_dt(value: datetime | str | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _time_decay_factor(now: datetime, review_time: datetime | None) -> float:
    if review_time is None:
        return 1.0
    age_days = max(0.0, (now - review_time).total_seconds() / 86400.0)
    factor = math.exp(-DECAY_LAMBDA_PER_DAY * age_days)
    return float(_clamp(factor, MIN_TIME_DECAY, 1.0))


def _apply_cache_decay(cache: dict[str, Any], now: datetime) -> dict[str, Any]:
    last = _parse_dt(cache.get("last_decay_at"))
    if last is None:
        cache["last_decay_at"] = now.isoformat()
        return cache

    elapsed_days = (now - last).total_seconds() / 86400.0
    if elapsed_days < 0.25:
        return cache

    factor = math.exp(-DECAY_LAMBDA_PER_DAY * max(0.0, elapsed_days))
    factor = float(_clamp(factor, MIN_TIME_DECAY, 1.0))
    for dimension in DIMENSIONS:
        cache[f"sum_weighted_{dimension}"] = float(cache.get(f"sum_weighted_{dimension}", 0.0) or 0.0) * factor
        cache[f"sum_weight_{dimension}"] = float(cache.get(f"sum_weight_{dimension}", 0.0) or 0.0) * factor
    cache["last_decay_at"] = now.isoformat()
    return cache


def _content_quality_factor(tokens: list[str], matched_dimension_count: int) -> float:
    word_count = len(tokens)
    if word_count >= 50 and matched_dimension_count >= 2:
        return 1.2
    if word_count >= 20:
        return 1.1
    return 1.0


def _consistency_factor(rating_score: int, sentiment_weight: float) -> float:
    if sentiment_weight == 0.0:
        return 1.0
    if rating_score <= 2 and sentiment_weight > 0:
        return 0.5
    if rating_score >= 4 and sentiment_weight < 0:
        return 0.5
    return 1.0


def _review_contribution(
    rating_score: int,
    comment: str | None,
    *,
    now: datetime,
    review_time: datetime | None,
) -> dict[str, tuple[float, float]] | None:
    if comment is None:
        return None

    text = _normalize_text(comment)
    tokens = _tokenize(text)

    matched_dimensions = [dimension for dimension, keywords in KEYWORDS.items() if any(keyword in text for keyword in keywords)]
    if not matched_dimensions:
        return None

    multiplier = _spam_multiplier(text, tokens, has_keyword=True)
    if multiplier is None:
        return None

    normalized_score = (float(rating_score) / 5.0) * 100.0
    sentiment_adjustment = _detect_sentiment_weight(text, tokens)
    adjusted_score = _clamp(normalized_score + sentiment_adjustment, 0.0, 100.0)

    quality = _content_quality_factor(tokens, matched_dimension_count=len(matched_dimensions))
    consistency = _consistency_factor(rating_score, sentiment_adjustment)
    time_decay = _time_decay_factor(now, review_time)

    review_weight_base = float(_clamp(quality * consistency * time_decay, 0.1, 2.0))
    review_multiplier = float(multiplier)

    contribution: dict[str, tuple[float, float]] = {}
    for dimension in matched_dimensions:
        contribution[dimension] = (
            adjusted_score * review_weight_base * review_multiplier,
            review_weight_base,
        )
    return contribution


def _default_cache() -> dict[str, Any]:
    cache: dict[str, Any] = {
        "total_reviews": 0,
        "unique_reviewers": 0,
        "last_review_at": None,
        "last_decay_at": None,
        "cache_version": CACHE_VERSION,
        "rating_history": [],
    }
    for dimension in DIMENSIONS:
        cache[f"sum_weighted_{dimension}"] = 0.0
        cache[f"sum_weight_{dimension}"] = 0.0
    return cache


def _ensure_cache(cache: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(cache, dict):
        return _default_cache()

    normalized = _default_cache()

    # migrate v1 cache fields (sum_*, count_*) → v2 (sum_weighted_*, sum_weight_*)
    for dimension in DIMENSIONS:
        if f"sum_{dimension}" in cache and f"sum_weighted_{dimension}" not in cache:
            normalized[f"sum_weighted_{dimension}"] = float(cache.get(f"sum_{dimension}", 0.0) or 0.0)
        if f"count_{dimension}" in cache and f"sum_weight_{dimension}" not in cache:
            normalized[f"sum_weight_{dimension}"] = float(cache.get(f"count_{dimension}", 0) or 0.0)

    for key, value in cache.items():
        normalized[key] = value
    normalized["cache_version"] = CACHE_VERSION
    return normalized


def _compute_snapshot(cache: dict[str, Any]) -> dict[str, float]:
    snapshot: dict[str, float] = {}
    for dimension in DIMENSIONS:
        weight_sum = float(cache.get(f"sum_weight_{dimension}", 0.0) or 0.0)
        total = float(cache.get(f"sum_weighted_{dimension}", 0.0) or 0.0)
        if weight_sum > 1e-9:
            score = _clamp(total / weight_sum, 0.0, 100.0)
        else:
            score = BASELINE_SCORE
        snapshot[dimension] = round(score, 2)
    return snapshot


def _level(score: float) -> str:
    if score < 40:
        return "low"
    if score < 70:
        return "medium"
    return "high"


def _compute_human_override(snapshot: dict[str, float]) -> dict[str, str]:
    return {
        "scenery_level": _level(snapshot["scenery"]),
        "accessibility_level": _level(snapshot["accessibility"]),
        "crowd_level": _level(snapshot["crowd"]),
        "value_level": _level(snapshot["value"]),
    }


def _compute_final_data(
    snapshot: dict[str, float],
    *,
    total_reviews: int,
    confidence: float,
    confidence_details: dict[str, Any],
) -> dict[str, Any]:
    scenery = snapshot["scenery"]
    accessibility = snapshot["accessibility"]
    crowd = snapshot["crowd"]
    value = snapshot["value"]

    real_score = (scenery * 0.35) + (accessibility * 0.25) + (value * 0.25) + (crowd * 0.15)
    final_score = (real_score * confidence) + (BASELINE_SCORE * (1.0 - confidence))

    if scenery > 70 and value > 60:
        summary = "Địa điểm có phong cảnh đẹp và giá trị trải nghiệm tốt."
    elif crowd < 40:
        summary = "Địa điểm khá đông đúc, nên cân nhắc thời gian ghé thăm."
    else:
        summary = "Địa điểm ở mức trung bình, phù hợp trải nghiệm cơ bản."

    show_details = confidence >= 0.4

    highlights: list[str] = []
    if show_details and scenery >= 70:
        highlights.append("Phong cảnh đẹp")
    if show_details and accessibility >= 70:
        highlights.append("Dễ di chuyển")
    if show_details and value >= 70:
        highlights.append("Giá hợp lý")
    if show_details and crowd >= 70:
        highlights.append("Không quá đông")

    risks: list[str] = []
    if show_details and crowd <= 40:
        risks.append("Đông đúc")
    if show_details and value <= 40:
        risks.append("Chi phí cao")
    if show_details and accessibility <= 40:
        risks.append("Khó tiếp cận")

    if final_score >= 75:
        recommendation = "Rất đáng đi"
    elif final_score >= 60:
        recommendation = "Có thể trải nghiệm"
    else:
        recommendation = "Cân nhắc trước khi đi"

    if total_reviews < 3:
        status = "insufficient_data"
    elif total_reviews < 10:
        status = "low_confidence"
    else:
        status = "reliable"

    if status == "reliable":
        spread = max(snapshot.values()) - min(snapshot.values())
        if spread >= 45:
            status = "high_variance"

    return {
        "score": round(final_score, 2),
        "real_score": round(real_score, 2),
        "confidence": round(confidence, 3),
        "confidence_details": confidence_details,
        "summary": summary,
        "highlights": highlights,
        "risks": risks,
        "recommendation": recommendation,
        "status": status,
    }


class InsightService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_insight(self, destination_id: int) -> DestinationInsight:
        insight = self.db.get(DestinationInsight, destination_id)
        if insight:
            return insight

        cache = _default_cache()
        snapshot = _compute_snapshot(cache)
        confidence_details = {
            "diversity_factor": 1.0,
            "recency_factor": 1.0,
            "unique_reviewers": 0,
            "total_reviews": 0,
        }
        insight = DestinationInsight(
            destination_id=destination_id,
            score_snapshot=snapshot,
            human_override=_compute_human_override(snapshot),
            final_data=_compute_final_data(snapshot, total_reviews=0, confidence=0.0, confidence_details=confidence_details),
            insight_cache=cache,
        )
        self.db.add(insight)
        self.db.flush()
        return insight

    def initialize_for_destination(self, destination_id: int) -> DestinationInsight:
        insight = self._ensure_insight(destination_id)

        cache = _default_cache()
        snapshot = _compute_snapshot(cache)
        confidence_details = {
            "diversity_factor": 1.0,
            "recency_factor": 1.0,
            "unique_reviewers": 0,
            "total_reviews": 0,
        }
        insight.score_snapshot = snapshot
        insight.human_override = _compute_human_override(snapshot)
        insight.final_data = _compute_final_data(snapshot, total_reviews=0, confidence=0.0, confidence_details=confidence_details)
        insight.insight_cache = cache
        self.db.flush()
        return insight

    def apply_rating_update(
        self,
        destination_id: int,
        new_score: int,
        new_comment: str | None,
        old_score: int | None = None,
        old_comment: str | None = None,
        *,
        new_review_time: datetime | str | None = None,
        old_review_time: datetime | str | None = None,
        is_new_rating: bool = False,
        reviewer_user_id: int | None = None,
    ) -> DestinationInsight:
        insight = self._ensure_insight(destination_id)
        cache = _ensure_cache(insight.insight_cache)

        now = _utc_now()
        cache = _apply_cache_decay(cache, now)

        old_contrib = None
        if old_score is not None and old_comment is not None:
            old_contrib = _review_contribution(
                old_score,
                old_comment,
                now=now,
                review_time=_parse_dt(old_review_time),
            )
            if old_contrib:
                for dimension, (sum_weighted_delta, weight_delta) in old_contrib.items():
                    cache[f"sum_weighted_{dimension}"] = float(cache.get(f"sum_weighted_{dimension}", 0.0) or 0.0) - float(
                        sum_weighted_delta
                    )
                    cache[f"sum_weight_{dimension}"] = float(cache.get(f"sum_weight_{dimension}", 0.0) or 0.0) - float(
                        weight_delta
                    )

        new_contrib = _review_contribution(
            new_score,
            new_comment,
            now=now,
            review_time=_parse_dt(new_review_time),
        )
        if new_contrib:
            for dimension, (sum_weighted_delta, weight_delta) in new_contrib.items():
                cache[f"sum_weighted_{dimension}"] = float(cache.get(f"sum_weighted_{dimension}", 0.0) or 0.0) + float(
                    sum_weighted_delta
                )
                cache[f"sum_weight_{dimension}"] = float(cache.get(f"sum_weight_{dimension}", 0.0) or 0.0) + float(
                    weight_delta
                )

        if is_new_rating:
            cache["total_reviews"] = max(int(cache.get("total_reviews", 0) or 0) + 1, 0)
            cache["unique_reviewers"] = max(int(cache.get("unique_reviewers", 0) or 0) + 1, 0)

        history = list(cache.get("rating_history", []))
        history.append(float(new_score))
        cache["rating_history"] = history[-100:]

        for dimension in DIMENSIONS:
            cache[f"sum_weight_{dimension}"] = max(float(cache.get(f"sum_weight_{dimension}", 0.0) or 0.0), 0.0)
            cache[f"sum_weighted_{dimension}"] = float(cache.get(f"sum_weighted_{dimension}", 0.0) or 0.0)

        cache["last_review_at"] = now.isoformat()
        cache["cache_version"] = CACHE_VERSION
        if reviewer_user_id is not None:
            cache["last_reviewer_user_id"] = int(reviewer_user_id)

        total_reviews = int(cache.get("total_reviews", 0) or 0)
        unique_reviewers = int(cache.get("unique_reviewers", 0) or 0)
        diversity_ratio = unique_reviewers / max(total_reviews, 1)
        diversity_factor = float(_clamp(0.8 + 0.4 * min(1.0, diversity_ratio / 0.7), 0.7, 1.2))

        last_review_at = _parse_dt(cache.get("last_review_at"))
        recency_factor = 1.0
        if last_review_at is not None:
            days = max(0.0, (now - last_review_at).total_seconds() / 86400.0)
            if days > 730:
                recency_factor = 0.8
            elif days > 365:
                recency_factor = 0.9

        rating_history = cache.get("rating_history", [])
        variance_factor = 1.0

        if len(rating_history) >= 3:
            variance = statistics.pvariance(rating_history)
            variance_factor = float(_clamp(1.0 - (variance / 8.0), 0.6, 1.0))

        confidence = min(
            1.0,
            (float(total_reviews) / 50.0)
            * diversity_factor
            * recency_factor
            * variance_factor,
        )

        confidence_details = {
            "diversity_factor": round(diversity_factor, 3),
            "recency_factor": round(recency_factor, 3),
            "unique_reviewers": unique_reviewers,
            "total_reviews": total_reviews,
            "variance_factor": round(variance_factor, 3),
        }

        snapshot = _compute_snapshot(cache)
        insight.score_snapshot = snapshot
        insight.human_override = _compute_human_override(snapshot)
        insight.final_data = _compute_final_data(
            snapshot,
            total_reviews=total_reviews,
            confidence=confidence,
            confidence_details=confidence_details,
        )
        insight.insight_cache = cache
        self.db.flush()
        return insight
