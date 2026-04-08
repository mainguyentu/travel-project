from __future__ import annotations

import re
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import DestinationInsight

BASELINE_SCORE = 50.0

DIMENSIONS = ("scenery", "accessibility", "crowd", "value")

KEYWORDS = {
    "scenery": ["đẹp", "view", "phong cảnh", "chill", "biển", "núi", "sống ảo"],
    "accessibility": ["dễ đi", "khó đi", "xa", "đường", "xe", "di chuyển"],
    "crowd": ["đông", "vắng", "chen", "quá tải"],
    "value": ["giá", "đắt", "rẻ", "phí", "dịch vụ"],
}

POSITIVE_WORDS = ["đẹp", "tốt", "ổn", "rẻ", "thuận tiện", "dễ"]
NEGATIVE_WORDS = ["đông", "đắt", "khó", "tệ", "xa", "chật"]
NEGATION_WORDS = ["không", "chưa", "ít"]

INTENSIFY_POSITIVE = ["rất đẹp"]
INTENSIFY_NEGATIVE = ["cực kỳ đông"]

AD_PHRASES = [
    "liên hệ",
    "zalo",
    "telegram",
    "facebook",
    "fb",
]

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


def _clamp(val: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, val))


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _tokenize(text: str) -> list[str]:
    tokens = []
    for raw in text.split():
        token = re.sub(r"[^\wÀ-ỹ]+", "", raw, flags=re.UNICODE)
        if token:
            tokens.append(token)
    return tokens


def _has_negation_before(tokens: list[str], index: int, window: int = 2) -> bool:
    start = max(0, index - window)
    return any(tokens[i] in NEGATION_WORDS for i in range(start, index))


def _detect_sentiment_weight(text: str, tokens: list[str]) -> float:
    for phrase in INTENSIFY_POSITIVE:
        if phrase in text:
            return 1.5
    for phrase in INTENSIFY_NEGATIVE:
        if phrase in text:
            return -1.5

    pos_found = False
    neg_found = False

    for idx, token in enumerate(tokens):
        if token in POSITIVE_WORDS:
            if _has_negation_before(tokens, idx):
                neg_found = True
            else:
                pos_found = True
        if token in NEGATIVE_WORDS:
            if _has_negation_before(tokens, idx):
                pos_found = True
            else:
                neg_found = True

    if pos_found and not neg_found:
        return 1.0
    if neg_found and not pos_found:
        return -1.0
    return 0.3


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


def _is_spam_language_or_emoji(text: str) -> bool:
    if EMOJI_RE.search(text):
        return True
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
    if _is_spam_language_or_emoji(normalized):
        return None

    return 1.0


def _review_contribution(rating_score: int, comment: str | None) -> dict[str, tuple[float, int]] | None:
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
    sentiment_weight = _detect_sentiment_weight(text, tokens) * multiplier

    contribution: dict[str, tuple[float, int]] = {}
    for dimension in matched_dimensions:
        contribution[dimension] = (normalized_score * sentiment_weight, 1)

    return contribution


def _default_cache() -> dict[str, Any]:
    cache: dict[str, Any] = {
        "total_reviews": 0,
    }
    for dimension in DIMENSIONS:
        cache[f"sum_{dimension}"] = 0.0
        cache[f"count_{dimension}"] = 0
    return cache


def _ensure_cache(cache: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(cache, dict):
        return _default_cache()
    normalized = _default_cache()
    for key, value in cache.items():
        normalized[key] = value
    return normalized


def _compute_snapshot(cache: dict[str, Any]) -> dict[str, float]:
    snapshot: dict[str, float] = {}
    for dimension in DIMENSIONS:
        count = int(cache.get(f"count_{dimension}", 0) or 0)
        total = float(cache.get(f"sum_{dimension}", 0.0) or 0.0)
        if count > 0:
            score = _clamp(total / count, 0.0, 100.0)
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


def _compute_final_data(snapshot: dict[str, float], total_reviews: int) -> dict[str, Any]:
    scenery = snapshot["scenery"]
    accessibility = snapshot["accessibility"]
    crowd = snapshot["crowd"]
    value = snapshot["value"]

    real_score = (scenery * 0.35) + (accessibility * 0.25) + (value * 0.25) + (crowd * 0.15)
    confidence = min(1.0, float(total_reviews) / 50.0)
    final_score = (real_score * confidence) + (BASELINE_SCORE * (1.0 - confidence))

    if scenery > 70 and value > 60:
        summary = "Địa điểm có phong cảnh đẹp và giá trị trải nghiệm tốt."
    elif crowd < 40:
        summary = "Địa điểm khá đông đúc, cần cân nhắc thời gian ghé thăm."
    else:
        summary = "Địa điểm ở mức trung bình, phù hợp trải nghiệm cơ bản."

    highlights: list[str] = []
    if scenery > 70:
        highlights.append("Phong cảnh đẹp")
    if accessibility > 70:
        highlights.append("Dễ di chuyển")
    if value > 70:
        highlights.append("Giá hợp lý")
    if crowd > 70:
        highlights.append("Không quá đông")

    risks: list[str] = []
    if crowd < 40:
        risks.append("Đông đúc")
    if value < 40:
        risks.append("Chi phí cao")
    if accessibility < 40:
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

    return {
        "score": round(final_score, 2),
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
        insight = DestinationInsight(
            destination_id=destination_id,
            score_snapshot=snapshot,
            human_override=_compute_human_override(snapshot),
            final_data=_compute_final_data(snapshot, total_reviews=0),
            insight_cache=cache,
        )
        self.db.add(insight)
        self.db.flush()
        return insight

    def initialize_for_destination(self, destination_id: int) -> DestinationInsight:
        insight = self._ensure_insight(destination_id)
        cache = _default_cache()
        snapshot = _compute_snapshot(cache)
        insight.score_snapshot = snapshot
        insight.human_override = _compute_human_override(snapshot)
        insight.final_data = _compute_final_data(snapshot, total_reviews=0)
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
        is_new_rating: bool = False,
    ) -> DestinationInsight:
        insight = self._ensure_insight(destination_id)
        cache = _ensure_cache(insight.insight_cache)

        old_contrib = None
        if old_score is not None and old_comment is not None:
            old_contrib = _review_contribution(old_score, old_comment)
            if old_contrib:
                for dimension, (sum_delta, count_delta) in old_contrib.items():
                    cache[f"sum_{dimension}"] = float(cache.get(f"sum_{dimension}", 0.0)) - sum_delta
                    cache[f"count_{dimension}"] = int(cache.get(f"count_{dimension}", 0)) - count_delta

        new_contrib = _review_contribution(new_score, new_comment)
        if new_contrib:
            for dimension, (sum_delta, count_delta) in new_contrib.items():
                cache[f"sum_{dimension}"] = float(cache.get(f"sum_{dimension}", 0.0)) + sum_delta
                cache[f"count_{dimension}"] = int(cache.get(f"count_{dimension}", 0)) + count_delta

        total_reviews = int(cache.get("total_reviews", 0))
        if is_new_rating and new_contrib:
            total_reviews += 1
        if not is_new_rating:
            if old_contrib and not new_contrib:
                total_reviews -= 1
            elif not old_contrib and new_contrib:
                total_reviews += 1
        cache["total_reviews"] = max(total_reviews, 0)

        for dimension in DIMENSIONS:
            cache[f"count_{dimension}"] = max(int(cache.get(f"count_{dimension}", 0)), 0)
            cache[f"sum_{dimension}"] = float(cache.get(f"sum_{dimension}", 0.0))

        snapshot = _compute_snapshot(cache)
        insight.score_snapshot = snapshot
        insight.human_override = _compute_human_override(snapshot)
        insight.final_data = _compute_final_data(snapshot, total_reviews=int(cache.get("total_reviews", 0)))
        insight.insight_cache = cache
        self.db.flush()
        return insight
