# Instructions: PII Redaction Pipeline

## End-to-End Pipeline Architecture
The pipeline architecture is broken down into 4 modular phases:

### Phase 1: Environment Setup & Initialization
- Set up the environment and install dependencies.
- Initialize `Presidio Analyzer` with a GPU-enabled spaCy transformer model (`en_core_web_trf`).
- Implement and register custom Indian context pattern recognizers (for PAN, Aadhaar, DOB, and Indian phone numbers) [1, 2].

### Phase 2: Stateful Synthetic Entity Generation
- Develop a stateful synthetic entity generation and mapping engine.
- Utilize `Faker` (with the `en_IN` locale) to generate realistic, referentially consistent substitute values.

### Phase 3: Document Parsing & OCR Engine
- Implement a document parser and OCR engine.
- Use `python-docx` for traversing XML paragraphs and tables within `.docx` files.
- Use `pytesseract` and `Pillow` to extract and process embedded raster ID cards (e.g., Aadhaar and PAN scans) [2].

### Phase 4: Replacement, Export, & Evaluation
- Implement formatting-preserving, in-place run replacement for text entities.
- Execute image blanking or substitution for detected PII in embedded raster images.
- Export the final redacted document to a new `.docx` file.
- Generate an automated token/entity evaluation report calculating Precision, Recall, and Accuracy against a ground-truth baseline [1].

## Architectural Constraints
- **In-place run-level text replacement**: Text modifications must operate at the run level to preserve original Word document formatting.
- **Descending character-offset string manipulation**: All string manipulations and text replacements must occur in descending character-offset order to avoid index corruption as string lengths change.
- **Zero data leakage**: The pipeline must ensure complete data redaction without leaving traces of the original PII.
