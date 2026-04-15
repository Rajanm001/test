import os
from pathlib import Path

from evaluator import evaluate_model
from compare import compare, generate_report

PROJECT_DIR = Path(__file__).parent
RESULTS_A = PROJECT_DIR / "results_model_a.csv"
RESULTS_B = PROJECT_DIR / "results_model_b.csv"
REPORT    = PROJECT_DIR / "report.md"


def main():
    model_a = os.getenv("EMAIL_ASSISTANT_MODEL_A", "gemini-2.5-flash")
    model_b = os.getenv("EMAIL_ASSISTANT_MODEL_B", "gemini-2.5-flash")

    label_a = f"{model_a} (few-shot)"
    label_b = f"{model_b} (zero-shot)"

    print("\n" + "=" * 60)
    print("EMAIL GENERATION ASSISTANT — EVALUATION PIPELINE")
    print("=" * 60)

    # --- Model A: few-shot prompting ---
    print(f"\n>> Evaluating {label_a}")
    evaluate_model(model_a, use_few_shot=True, output_csv=str(RESULTS_A))

    # --- Model B: zero-shot baseline ---
    print(f"\n>> Evaluating {label_b}")
    evaluate_model(model_b, use_few_shot=False, output_csv=str(RESULTS_B))

    # --- Comparison ---
    print("\n>> Comparing results")
    result = compare(RESULTS_A, RESULTS_B, label_a, label_b)
    generate_report(result, RESULTS_A, RESULTS_B, label_a, label_b, str(REPORT))

    print("\nDone. Output files:")
    print(f"  - {RESULTS_A.name}")
    print(f"  - {RESULTS_B.name}")
    print(f"  - {REPORT.name}")


if __name__ == "__main__":
    main()
