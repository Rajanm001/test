import json
from pathlib import Path

import pandas as pd

from generator import generate_email
from metrics import fact_recall_score, tone_accuracy_score, conciseness_score, compute_overall

DATA_DIR = Path(__file__).parent
TEST_DATA = DATA_DIR / "test_data.json"


def load_scenarios():
    with open(TEST_DATA, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_model(model_name, use_few_shot=True, output_csv=None):
    """Run all test scenarios, score each email, and save results to CSV."""
    scenarios = load_scenarios()
    records = []

    for idx, sc in enumerate(scenarios, 1):
        print(f"  [{idx}/{len(scenarios)}] {sc['intent'][:55]}...")

        email = generate_email(
            intent=sc["intent"],
            facts=sc["facts"],
            tone=sc["tone"],
            model=model_name,
            use_few_shot=use_few_shot,
        )

        fr = fact_recall_score(sc["facts"], email)
        ta = tone_accuracy_score(email, sc["tone"])
        cs = conciseness_score(email)
        ov = compute_overall(fr, ta, cs)

        records.append({
            "scenario_id": idx,
            "intent": sc["intent"],
            "tone": sc["tone"],
            "generated_email": email,
            "fact_recall": fr,
            "tone_accuracy": ta,
            "conciseness": cs,
            "overall": ov,
        })

    df = pd.DataFrame(records)

    if output_csv:
        csv_path = Path(output_csv)
    else:
        tag = model_name.replace("-", "_")
        csv_path = DATA_DIR / f"results_{tag}.csv"

    df.to_csv(csv_path, index=False)
    print(f"  Saved {len(records)} results -> {csv_path.name}")
    return df
