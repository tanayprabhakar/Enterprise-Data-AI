"""
evaluate.py — Standalone evaluation for the PII redaction pipeline.

Ground truth is human-verified from the first 5 pages of the DRHP.
Run against golden_test_sample.docx for apples-to-apples scoring.
"""
import json

GROUND_TRUTH = {
    "PERSON": [
        "Kushal Subbayya Hegde",
        "Pushpa Kushal Hegde",
        "Rajesh Kushal Hegde",
        "Rohit Kushal Hegde",
        "VISHAL SINGH",
        "SUGRIV SINGH",
        "MERAJ KHAN",
        "Sudhdan Khan",
    ],
    "IN_PAN": [
        "NBWPS1951N",
    ],
    "IN_AADHAAR": [
        "2943 6593 3461",
    ],
    "DATE_OF_BIRTH": [
        "06/05/2000",
        "12/12/1988",
    ],
}


def score(detections: list, ground_truth: dict = GROUND_TRUTH) -> dict:
    """
    Compute per-entity-type and overall Precision, Recall, F1-Score.

    Parameters
    ----------
    detections : list of (text, entity_type) tuples from the pipeline.
    ground_truth : dict mapping entity types to lists of known PII strings.

    Returns
    -------
    dict with per-type and OVERALL metrics.
    """
    pred_by_type = {k: [] for k in ground_truth}
    for text, label in detections:
        if label in pred_by_type:
            pred_by_type[label].append(text)

    results = {}
    total_tp = total_fp = total_fn = 0

    for etype, truth_list in ground_truth.items():
        truth_set = {t.strip().lower() for t in truth_list}
        pred_set = {p.strip().lower() for p in pred_by_type[etype]}

        tp = len(truth_set & pred_set)
        fp = len(pred_set - truth_set)
        fn = len(truth_set - pred_set)

        prec = tp / (tp + fp) if (tp + fp) else 1.0
        rec = tp / (tp + fn) if (tp + fn) else 1.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

        results[etype] = {
            "TP": tp, "FP": fp, "FN": fn,
            "precision": round(prec, 3),
            "recall": round(rec, 3),
            "f1_score": round(f1, 3),
        }
        total_tp += tp
        total_fp += fp
        total_fn += fn

    p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 1.0
    r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 1.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0

    results["OVERALL"] = {
        "TP": total_tp, "FP": total_fp, "FN": total_fn,
        "precision": round(p, 3),
        "recall": round(r, 3),
        "f1_score": round(f, 3),
    }
    return results


if __name__ == "__main__":
    # Dry-run with example predictions to verify the math
    example_detections = [
        ("Kushal Subbayya Hegde", "PERSON"),
        ("Pushpa Kushal Hegde", "PERSON"),
        ("Rajesh Kushal Hegde", "PERSON"),
        ("Rohit Kushal Hegde", "PERSON"),
        ("NBWPS1951N", "IN_PAN"),
        ("2943 6593 3461", "IN_AADHAAR"),
        ("06/05/2000", "DATE_OF_BIRTH"),
        ("12/12/1988", "DATE_OF_BIRTH"),
        # Simulated false positives
        ("John Random", "PERSON"),
    ]
    print(json.dumps(score(example_detections), indent=2))
