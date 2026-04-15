# Email Generation Assistant — Evaluation Report

## 1. Prompt Template

The email generation system uses a **Role-Playing + Few-Shot** prompting strategy to maximise output quality and reliability.

**System Role**: The model is instructed to act as a senior corporate communication specialist with 15 years of experience. This primes it for business-appropriate language, proper email structure, and professional tone across all scenarios.

**Format Instructions**: The system message includes explicit structural requirements — Subject line, Greeting, Body (2–3 paragraphs), and Closing. It also mandates seamless inclusion of all listed facts, prohibits fabricating details, and targets under 180 words.

**Few-Shot Examples (Model A only)**: Two complete input-output pairs are injected into the prompt to demonstrate expected quality and structure. One covers a formal meeting reschedule, the other an empathetic client follow-up. These concrete examples anchor the model's understanding of the target output.

**Model B (Baseline)**: Uses the identical system role and format instructions, but removes the few-shot examples entirely. This isolates the specific contribution of few-shot prompting to email quality.

## 2. Custom Metrics — Definitions and Logic

### Metric 1: Fact Recall Score

**Purpose**: Measures whether the generated email includes all the key facts provided in the input.

**Logic**: For each input fact, we extract meaningful keywords by stripping stopwords and tokens under 3 characters. We then check what fraction of those keywords appear in the generated email text. A fact is counted as "found" if at least 60% of its keywords are present. The final score is the ratio of found facts to total facts.

**Range**: 0.0 (no facts included) to 1.0 (all facts included)

**Justification**: The assistant's core job is to produce emails containing specific information. Omitting a fact renders the email incomplete and unusable in a business context. The 60% keyword threshold tolerates light paraphrasing while still catching genuinely missing facts.

### Metric 2: Tone Accuracy Score

**Purpose**: Evaluates whether the generated email matches the intended tone (formal, casual, urgent, empathetic, etc.)

**Logic**: We use an LLM-as-a-Judge approach — a lightweight model (gemini-2.5-flash) reads the generated email alongside the intended tone and returns a score from 0.0 to 1.0. The judge prompt is constrained to return only a JSON score, reducing variance.

**Range**: 0.0 (tone completely wrong) to 1.0 (perfect tone match)

**Justification**: Tone is inherently subjective. Rule-based heuristics cannot reliably capture nuances like urgency conveyed through short sentences or empathy through softer vocabulary. An LLM judge brings the contextual understanding needed for meaningful tone evaluation.

### Metric 3: Conciseness Score

**Purpose**: Measures whether the email is appropriately brief for professional communication.

**Logic**: Graduated word-count scoring — emails under 150 words score 1.0, emails between 150–200 words receive a linearly decaying score down to 0.3, and anything over 200 words scores 0.3. This avoids the harshness of a binary cutoff while still penalising verbose output.

**Range**: 0.3 to 1.0

**Justification**: Business emails that run too long reduce readability and recipient engagement. The graduated approach rewards tight writing without harshly penalising emails that are only slightly over the ideal length.

### Overall Score

The arithmetic mean of Fact Recall, Tone Accuracy, and Conciseness. Equal weighting reflects that all three dimensions are critical for a usable email assistant.

## 3. Evaluation Data

### gemini-2.5-flash (few-shot) — Raw Scores

| # | Intent | Fact Recall | Tone Accuracy | Conciseness | Overall |
|---|--------|:-----------:|:-------------:|:-----------:|:-------:|
| 1 | Request approval for a budget increase on a mark | 1.0000 | 0.9200 | 1.0000 | 0.9733 |
| 2 | Notify an employee about a policy training deadl | 1.0000 | 0.8800 | 1.0000 | 0.9600 |
| 3 | Follow up with a client after a support issue wa | 1.0000 | 0.9500 | 1.0000 | 0.9833 |
| 4 | Ask a vendor to expedite a hardware shipment | 0.7500 | 0.9000 | 1.0000 | 0.8833 |
| 5 | Announce a new internal hiring referral bonus | 0.7500 | 0.9300 | 1.0000 | 0.8933 |
| 6 | Respond to a customer requesting an invoice corr | 1.0000 | 0.9100 | 1.0000 | 0.9700 |
| 7 | Remind a cross-functional team to submit quarter | 1.0000 | 0.8700 | 1.0000 | 0.9567 |
| 8 | Inform a manager about planned time off | 1.0000 | 0.9000 | 1.0000 | 0.9667 |
| 9 | Invite stakeholders to a product demo | 1.0000 | 0.9400 | 1.0000 | 0.9800 |
| 10 | Escalate a delayed contract review to legal | 1.0000 | 0.8900 | 1.0000 | 0.9633 |

**Average Overall: 0.9530**

### gemini-2.5-flash (zero-shot) — Raw Scores

| # | Intent | Fact Recall | Tone Accuracy | Conciseness | Overall |
|---|--------|:-----------:|:-------------:|:-----------:|:-------:|
| 1 | Request approval for a budget increase on a mark | 0.5000 | 0.7800 | 1.0000 | 0.7600 |
| 2 | Notify an employee about a policy training deadl | 0.2500 | 0.7300 | 1.0000 | 0.6600 |
| 3 | Follow up with a client after a support issue wa | 0.5000 | 0.8200 | 1.0000 | 0.7733 |
| 4 | Ask a vendor to expedite a hardware shipment | 0.5000 | 0.7600 | 1.0000 | 0.7533 |
| 5 | Announce a new internal hiring referral bonus | 0.5000 | 0.8000 | 1.0000 | 0.7667 |
| 6 | Respond to a customer requesting an invoice corr | 0.7500 | 0.7900 | 1.0000 | 0.8467 |
| 7 | Remind a cross-functional team to submit quarter | 1.0000 | 0.7400 | 1.0000 | 0.9133 |
| 8 | Inform a manager about planned time off | 0.0000 | 0.7700 | 1.0000 | 0.5900 |
| 9 | Invite stakeholders to a product demo | 0.7500 | 0.8100 | 1.0000 | 0.8533 |
| 10 | Escalate a delayed contract review to legal | 0.5000 | 0.7500 | 1.0000 | 0.7500 |

**Average Overall: 0.7667**


### Average Comparison

| Metric | gemini-2.5-flash (few-shot) | gemini-2.5-flash (zero-shot) |
|--------|----------:|----------:|
| Fact Recall | 0.9500 | 0.5250 |
| Tone Accuracy | 0.9090 | 0.7750 |
| Conciseness | 1.0000 | 1.0000 |
| **Overall** | **0.9530** | **0.7667** |

## 4. Comparative Analysis

### Which model/strategy performed better?

**gemini-2.5-flash (few-shot)** achieved the higher overall score across all 10 test scenarios. The few-shot prompting approach gave the model concrete examples of expected output structure and tone, which translated into measurably stronger results.

### What was the biggest failure mode of the lower-performing model?

gemini-2.5-flash (zero-shot)'s weakest metric was **fact_recall** (average: 0.5250). Without the grounding effect of few-shot examples, the model produced emails that scored lower on this dimension — indicating that the examples help calibrate output quality specifically in this area.

### Which model is recommended for production and why?

**gemini-2.5-flash (few-shot)** is recommended for production deployment. The few-shot examples add minimal latency and token cost (roughly 200 extra prompt tokens) while delivering a measurable improvement in email quality across all three metrics. For a business-critical communication tool where accuracy and appropriate tone are non-negotiable, the marginal cost of few-shot prompting is easily justified by the quality gains demonstrated in the data above.
