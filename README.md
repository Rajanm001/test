# Email Generation Assistant

> An end-to-end pipeline that generates professional business emails using Google Gemini, evaluates them against three custom metrics, and compares prompting strategies with a reproducible benchmark.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-API-4285F4?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

The Email Generation Assistant takes three structured inputs — **intent**, **key facts**, and **tone** — and produces a ready-to-send professional email. It includes a complete evaluation framework that scores generated emails on factual accuracy, tone alignment, and conciseness, then compares two prompting strategies head-to-head across 10 diverse business scenarios.

### Key Results

| Strategy | Fact Recall | Tone Accuracy | Conciseness | Overall |
|----------|:-----------:|:-------------:|:-----------:|:-------:|
| **Few-Shot** | 0.9500 | 0.9090 | 1.0000 | **0.9530** |
| Zero-Shot | 0.5250 | 0.7750 | 1.0000 | 0.7667 |

Few-shot prompting delivers a **24.3% improvement** in overall quality over the zero-shot baseline, with the largest gains in fact recall (+81%) and tone accuracy (+17%).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│              (orchestrates the full pipeline)                │
├─────────────┬─────────────────────┬─────────────────────────┤
│             │                     │                         │
│   ┌─────────▼──────────┐  ┌──────▼──────────┐  ┌──────────▼─────────┐
│   │   evaluator.py     │  │   compare.py    │  │    report.md       │
│   │  (10-scenario loop)│  │ (metric diff +  │  │  (auto-generated   │
│   │                    │  │  winner select) │  │   analysis doc)    │
│   └────────┬───────────┘  └─────────────────┘  └────────────────────┘
│            │
│   ┌────────▼───────────┐
│   │   generator.py     │──── Gemini API ──── gemini-2.5-flash
│   │  (email generation │
│   │   + rate limiting) │
│   └────────┬───────────┘
│            │
│   ┌────────▼───────────┐
│   │    prompts.py      │
│   │ (role + format +   │
│   │  few-shot examples)│
│   └────────────────────┘
│            │
│   ┌────────▼───────────┐
│   │    metrics.py      │
│   │ (fact_recall +     │
│   │  tone_accuracy +   │
│   │  conciseness)      │
│   └────────────────────┘
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
email_assistant_project/
├── main.py              # Entry point — runs the full evaluation pipeline
├── generator.py         # Email generation via Google Gemini API with retry + rate limiting
├── prompts.py           # Prompt engineering: system role, format rules, few-shot examples
├── evaluator.py         # Evaluation loop across 10 test scenarios
├── metrics.py           # Three custom scoring metrics + LLM-as-a-Judge
├── compare.py           # Statistical comparison and Markdown report generation
├── test_data.json       # 10 curated business email scenarios with human references
├── requirements.txt     # Python dependencies
├── report.md            # Auto-generated evaluation report with full analysis
├── results_model_a.csv  # Model A per-scenario scores (auto-generated)
└── results_model_b.csv  # Model B per-scenario scores (auto-generated)
```

---

## Quick Start

**Prerequisites**: Python 3.10+ and a [Google Gemini API key](https://aistudio.google.com/apikey) (free tier works).

```bash
# 1. Clone
git clone https://github.com/Rajanm001/test.git
cd test

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key
# Linux / macOS
export GEMINI_API_KEY="your-key-here"
# Windows (PowerShell)
$env:GEMINI_API_KEY = "your-key-here"
# Windows (CMD)
set GEMINI_API_KEY=your-key-here

# 4. Run the full pipeline
python main.py
```

The pipeline will:
1. Generate emails for all 10 scenarios using **Model A** (few-shot prompting)
2. Generate emails for the same scenarios using **Model B** (zero-shot baseline)
3. Score every email on three custom metrics
4. Output `results_model_a.csv`, `results_model_b.csv`, and a detailed `report.md`

---

## Prompt Engineering Strategy

The system uses a **Role-Playing + Few-Shot** approach designed to maximize factual accuracy and tone consistency:

| Layer | Purpose | Implementation |
|-------|---------|----------------|
| **System Role** | Primes the model for business-grade language | 15-year corporate communication specialist persona |
| **Format Instructions** | Enforces consistent email structure | Subject → Greeting → Body (2-3 paragraphs) → Closing |
| **Fact Mandate** | Prevents hallucination | Explicit rule: include every listed fact, fabricate nothing |
| **Few-Shot Examples** | Anchors output quality with concrete demonstrations | 2 curated input-output pairs (formal + empathetic tones) |
| **Brevity Target** | Keeps emails focused and professional | Under 180 words directive |

**Model B** uses the identical configuration but strips the few-shot examples, isolating their contribution to quality.

---

## Custom Evaluation Metrics

### 1. Fact Recall Score

Measures whether all required facts appear in the generated email.

- **Method**: Extract meaningful keywords from each input fact (after removing stopwords and short tokens). A fact is "found" if ≥60% of its keywords appear in the email.
- **Score**: `facts_found / total_facts` — range `[0.0, 1.0]`
- **Why**: The assistant's primary job is to communicate specific information. Missing a fact makes the email unusable.

### 2. Tone Accuracy Score

Evaluates whether the email matches the requested tone (formal, urgent, empathetic, etc.).

- **Method**: LLM-as-a-Judge — a separate Gemini call reads the email alongside the intended tone and returns a `0.0–1.0` score. The judge prompt is constrained to JSON-only output to reduce variance.
- **Score**: Range `[0.0, 1.0]`
- **Why**: Tone is inherently subjective. Rule-based heuristics miss nuances like urgency communicated through sentence pacing or empathy through vocabulary softening. An LLM judge captures these contextual signals.

### 3. Conciseness Score

Measures whether the email is appropriately brief for professional communication.

- **Method**: Graduated word-count scoring:
  - ≤ 150 words → `1.0`
  - 150–200 words → linear decay from `1.0` to `0.3`
  - \> 200 words → `0.3`
- **Score**: Range `[0.3, 1.0]`
- **Why**: Overly long emails reduce readability and engagement. The graduated approach rewards tight writing without being punitive at the boundary.

### Overall Score

Arithmetic mean of all three metrics. Equal weighting reflects that factual completeness, tone alignment, and brevity are all essential for production-quality email generation.

---

## Test Scenarios

The evaluation covers 10 diverse corporate communication types:

| # | Scenario | Tone |
|---|----------|------|
| 1 | Budget increase approval request | Formal |
| 2 | Policy training deadline notification | Clear & Formal |
| 3 | Client support issue follow-up | Empathetic |
| 4 | Vendor hardware shipment expedite | Urgent |
| 5 | Internal referral bonus announcement | Enthusiastic |
| 6 | Customer invoice correction response | Professional & Apologetic |
| 7 | Cross-functional quarterly update reminder | Direct |
| 8 | Manager time-off notification | Polite |
| 9 | Stakeholder product demo invitation | Friendly |
| 10 | Legal contract review escalation | Firm & Professional |

Each scenario includes a hand-written human reference email for qualitative benchmarking.

---

## Configuration

Override default models via environment variables:

```bash
# Use different Gemini models
$env:EMAIL_ASSISTANT_MODEL_A = "gemini-2.5-flash"
$env:EMAIL_ASSISTANT_MODEL_B = "gemini-2.5-flash"
python main.py
```

Rate limiting is built in (13-second intervals between API calls) to stay within the Gemini free-tier quota of 5 requests/minute.

---

## Output Files

| File | Description |
|------|-------------|
| `results_model_a.csv` | Per-scenario scores and generated emails for Model A (few-shot) |
| `results_model_b.csv` | Per-scenario scores and generated emails for Model B (zero-shot) |
| `report.md` | Complete evaluation report: metric definitions, raw data tables, comparative analysis, and production recommendation |

---

## License

MIT
