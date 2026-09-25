"""
Evaluation script for the DRHP PII redaction pipeline.
Run only against golden_test_sample.docx (5 curated pages), never the full
400-page document, so precision/recall numbers are apples-to-apples.
"""

GROUND_TRUTH_BASELINE = {
    "promoter_names": [
        "Kushal Subbayya Hegde",
        "Pushpa Kushal Hegde",
        "Rajesh Kushal Hegde",
        "Rohit Kushal Hegde",
    ],
    "pan_numbers": [
        "NBWPS1951N",
    ],
    "pan_card_details": {
        "name": "VISHAL SINGH",
        "father_name": "SUGRIV SINGH",
        "pan": "NBWPS1951N",
        "dob": "06/05/2000",
    },
    "aadhaar_numbers": [
        "2943 6593 3461",
    ],
    "aadhaar_card_details": {
        "name": "MERAJ KHAN",
        "father_name": "Sudhdan Khan",
        "aadhaar": "2943 6593 3461",
        "dob": "12/12/1988",
        "address": "saray dan shah, KATRAULI, Poore Durgi, Phoolpur, Allahabad, Uttar Pradesh, 212402",
    },
    "regulatory_terms": [
        "Qualified Institutional Buyer(s)",
        "QIB(s)",
        "QIB Bidder(s)",
    ],
    "newspaper_names": [
        "Financial Express",
        "Jansatta",
        "Loksatta",
    ],
}


def score(predicted: dict, ground_truth: dict = GROUND_TRUTH_BASELINE) -> dict:
    """
    Compare the pipeline's output against GROUND_TRUTH_BASELINE.
    `predicted` should use the same keys, each a list/dict of extracted values.
    Returns per-category precision/recall plus overall totals.
    """
    results = {}
    total_tp = total_fp = total_fn = 0

    for key, truth_val in ground_truth.items():
        truth_set = (
            set(truth_val.values()) if isinstance(truth_val, dict) else set(truth_val)
        )
        pred_val = predicted.get(key, [] if isinstance(truth_val, list) else {})
        pred_set = (
            set(pred_val.values()) if isinstance(pred_val, dict) else set(pred_val)
        )

        tp = len(truth_set & pred_set)
        fp = len(pred_set - truth_set)
        fn = len(truth_set - pred_set)

        precision = tp / (tp + fp) if (tp + fp) else 1.0
        recall = tp / (tp + fn) if (tp + fn) else 1.0

        results[key] = {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
        }
        total_tp += tp
        total_fp += fp
        total_fn += fn

    overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 1.0
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 1.0

    results["overall"] = {
        "true_positives": total_tp,
        "false_positives": total_fp,
        "false_negatives": total_fn,
        "precision": round(overall_precision, 3),
        "recall": round(overall_recall, 3),
    }
    return results


if __name__ == "__main__":
    # Example: replace this with your pipeline's actual output on
    # golden_test_sample.docx before running.
    example_predicted = {
        "promoter_names": ["Kushal Subbayya Hegde", "Pushpa Kushal Hegde"],
        "pan_numbers": ["NBWPS1951N"],
        "aadhaar_numbers": [],
    }
    import json
    print(json.dumps(score(example_predicted), indent=2))
