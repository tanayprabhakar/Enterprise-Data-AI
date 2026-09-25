# PII Redaction Tool — Indian DRHP Documents

## Approach

This pipeline combines **Presidio Analyzer** (backed by SpaCy's `en_core_web_trf`
transformer model) with **custom regex recognizers** and **Faker** for synthetic
data replacement.

| Layer | What it handles |
|-------|-----------------|
| SpaCy NER (`en_core_web_trf`) | PERSON, ORGANIZATION, LOCATION detection |
| Custom Presidio `PatternRecognizer` | PAN, Aadhaar, CIN, SEBI Reg, DOB, Indian phone numbers, PIN codes, SSN, credit cards, URLs |
| Allowlist post-filter | Prevents false positives on regulatory bodies (SEBI, BSE, NSE), statutory terms (QIB, NII), state/country names used in legal context, and newspaper names in publication clauses |
| Faker `PII_REGISTRY` | Ensures the same real PII string always maps to the same fake replacement across the entire document |
| Tesseract OCR | Extracts text from embedded PAN/Aadhaar card images for redaction |

### Design decisions

- **Sentence-casing** (`text.capitalize()`) is applied to all-caps legal headings
  before NER analysis. This prevents SpaCy from interpreting every capitalised
  common noun (e.g. "DETAILS", "OFFER", "PUBLIC") as a named entity.

- **Allowlist** instead of blanket paragraph-skipping. Earlier versions skipped
  entire paragraphs containing "NEWSPAPER" or "FINANCIAL EXPRESS", which leaked
  any real PII that happened to sit in the same paragraph. The current version
  inspects every token but protects specific allowlisted terms from redaction.

- **PIN Code context guard**: 6-digit Indian PIN codes match an enormous number
  of false positives (page numbers, section references, financial figures). The
  pipeline only redacts a 6-digit match when it appears near address-related
  keywords (PIN, ADDRESS, ROAD, NAGAR, etc.).

- **Image redaction**: Embedded ID card images are OCR'd with Tesseract, the
  extracted text is redacted, and the original image is replaced in-place with a
  white canvas showing the redacted text. No raw text dump is appended to the
  document.

## Trade-offs & Known Limitations

| # | Issue | Status |
|---|-------|--------|
| 1 | SpaCy may still flag some company names as PERSON (e.g. "Nuvama Wealth") | Accepted — erring on the side of recall |
| 2 | Tesseract OCR on low-quality scans may miss glued characters | Mitigated with `re.sub(r'([a-z])([A-Z])', ...)` ungluing |
| 3 | Aadhaar addresses on ID cards may only be partially captured by NER | Mitigated — full OCR text goes through `redact_text_block` |
| 4 | Credit cards / SSNs are unlikely in Indian DRHPs but recognizers are included per the assignment spec | No false positives expected |

## Evaluation Approach

A **human-checked ground truth** was manually compiled from the first 5 pages of
the DRHP. Each PII instance was read and recorded by hand, covering: promoter
names, PAN numbers, Aadhaar numbers, dates of birth, and OCR-extracted names
from embedded ID card images.

The evaluation function (`score()`) compares pipeline detections against this
ground truth using **case-insensitive set intersection**:

- **True Positive (TP)**: entity in both ground truth and predictions
- **False Positive (FP)**: entity in predictions but not ground truth
- **False Negative (FN)**: entity in ground truth but not predictions

Metrics are computed per entity type and overall:

```
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1-Score  = 2 × Precision × Recall / (Precision + Recall)
```

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_trf
apt-get install tesseract-ocr   # Linux

# 2. Place your DRHP at:
#    data/input/Red Herring Prospectus.docx

# 3. Run the notebook (Google Colab recommended for GPU)
#    Open pii_redactor.ipynb and run all cells.
#    Output: data/output/Anonymized_Red_Herring_Prospectus.docx

# 4. Run standalone evaluation (optional)
python evaluate.py
```

## File Structure

```
├── pii_redactor.ipynb         # Main pipeline (7 cells)
├── evaluate.py                # Standalone evaluation script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── data/
│   ├── input/                 # Place source DRHP here
│   └── output/                # Redacted output goes here
└── .gitignore                 # Excludes .docx and data/ from VCS
```
