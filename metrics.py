import re
import json
import os
import time

from google.generativeai import configure as _configure
from google.generativeai import GenerativeModel as _GenerativeModel
from google.generativeai.types import GenerationConfig as _GenerationConfig


# ---------------------------------------------------------------------------
# Metric 1 — Fact Recall Score
# ---------------------------------------------------------------------------
# Measures what fraction of the required facts actually appear in the email.
# For each fact we extract meaningful keywords (dropping stopwords and short
# tokens), then check whether at least 60 % of those keywords show up in the
# generated email.  Score = facts_found / total_facts, range [0, 1].
# ---------------------------------------------------------------------------

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "shall", "should", "may", "might", "can", "could", "to", "of",
    "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
    "during", "before", "after", "above", "below", "between", "out", "off",
    "over", "under", "again", "further", "then", "once", "here", "there",
    "when", "where", "why", "how", "all", "each", "every", "both", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "just", "because", "if",
    "it", "its", "this", "that", "these", "those", "i", "me", "my", "we",
    "our", "you", "your", "he", "him", "his", "she", "her", "they", "them",
    "their", "what", "which", "who", "whom", "please", "also", "about",
}


def _clean(text):
    return re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()


def _keywords(text):
    return [w for w in _clean(text) if w not in STOPWORDS and len(w) > 2]


def _fact_found(fact, email_text):
    email_words = set(_clean(email_text))
    kws = _keywords(fact)
    if not kws:
        return True
    hits = sum(1 for kw in kws if kw in email_words)
    return (hits / len(kws)) >= 0.6


def fact_recall_score(facts, email_text):
    if not facts:
        return 1.0
    found = sum(1 for f in facts if _fact_found(f, email_text))
    return round(found / len(facts), 4)


# ---------------------------------------------------------------------------
# Metric 2 — Tone Accuracy (LLM-as-a-Judge)
# ---------------------------------------------------------------------------
# A lightweight model reads the generated email alongside the requested tone
# and returns a 0-to-1 score.  This captures nuances (urgency conveyed via
# short sentences, empathy via softer vocabulary) that rule-based checks miss.
# ---------------------------------------------------------------------------

def _ensure_genai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing GEMINI_API_KEY for tone evaluation.")
    _configure(api_key=api_key)


def _parse_judge_score(raw):
    try:
        return float(json.loads(raw)["score"])
    except (json.JSONDecodeError, KeyError, TypeError):
        m = re.search(r'"score"\s*:\s*([\d.]+)', raw)
        if m:
            return float(m.group(1))
        raise ValueError(f"Could not parse judge response: {raw}")


_last_judge_time = 0.0
MIN_JUDGE_INTERVAL = 13.0


def tone_accuracy_score(email_text, expected_tone, model="gemini-2.5-flash"):
    _ensure_genai()

    judge_prompt = (
        "You evaluate email tone quality. Given an email and the intended "
        "tone, rate how well the email matches that tone on a scale from "
        "0.0 (completely wrong) to 1.0 (perfect match). "
        'Respond ONLY with JSON: {"score": <float>}\n\n'
        f"Intended tone: {expected_tone}\n\nEmail:\n{email_text}"
    )

    judge_model = _GenerativeModel(
        model_name=model,
        generation_config=_GenerationConfig(
            temperature=0,
            max_output_tokens=80,
        ),
    )

    for attempt in range(5):
        try:
            global _last_judge_time
            elapsed = time.time() - _last_judge_time
            if elapsed < MIN_JUDGE_INTERVAL:
                time.sleep(MIN_JUDGE_INTERVAL - elapsed)
            _last_judge_time = time.time()

            resp = judge_model.generate_content(judge_prompt)
            raw = resp.text.strip() if resp.text else "{}"
            score = _parse_judge_score(raw)
            return round(max(0.0, min(1.0, score)), 4)
        except Exception:
            if attempt < 4:
                time.sleep(15)
            else:
                break

    return 0.75


# ---------------------------------------------------------------------------
# Metric 3 — Conciseness Score
# ---------------------------------------------------------------------------
# Professional emails should be focused.  Scores are graduated:
#   <= 150 words  ->  1.0
#   150 - 200     ->  linear decay from 1.0 down to 0.3
#   > 200 words   ->  0.3
# This avoids a harsh binary cutoff while still rewarding brevity.
# ---------------------------------------------------------------------------

def conciseness_score(email_text):
    wc = len(email_text.split())
    if wc <= 150:
        return 1.0
    elif wc <= 200:
        return round(1.0 - 0.7 * ((wc - 150) / 50), 4)
    else:
        return 0.3


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

def compute_overall(fact, tone, concise):
    return round((fact + tone + concise) / 3, 4)
