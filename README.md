# GDPR Guardian

> A Python proof of concept for best-effort detection and redaction of selected identifiers in German-language text.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![NLP](https://img.shields.io/badge/NLP-spaCy-green)
![CI](https://github.com/osmankaankars/GDPR-Guardian/actions/workflows/ci.yml/badge.svg)

## Scope

The prototype combines regular expressions with spaCy's small German model:

- Austrian IBANs in the supported `AT..` layout.
- Phone-number patterns beginning with `+43`, `+49`, or `0`.
- Email-address patterns.
- Person (`PER`) and location (`LOC`) entities returned by `de_core_news_sm`.
- Plain-text input and text extraction from PDFs.

Matches are replaced with explicit placeholders such as `[EMAIL_REDACTED]`, `[PERSON_GDPR]`, and `[LOCATION_GDPR]`. PDF input is extracted and written as plain text; the project does not preserve PDF layout or create a redacted PDF document.

## Install

```bash
git clone https://github.com/osmankaankars/GDPR-Guardian.git
cd GDPR-Guardian
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The pinned requirements include the `de_core_news_sm` model. If you install spaCy separately, install the model with:

```bash
python -m spacy download de_core_news_sm
```

## Use

```bash
python anonymizer.py kunde_wien.txt
```

`kunde_wien.txt` is a synthetic fixture for local demonstration.

For text input, the result is written to `redacted_<input-name>`. For PDF input, extracted and redacted text is written to `redacted_<input-stem>.txt`. Output is created in the current working directory rather than beside the source file. An existing file with the same generated name can be overwritten, so use a separate working directory for important data.

Example input:

```text
Client: Hans Müller, Location: Wien, IBAN: AT89 3704 0044 0532 0130
```

Possible output, depending on the NLP model's entity detection:

```text
Client: [PERSON_GDPR], Location: [LOCATION_GDPR], IBAN: [IBAN_REDACTED]
```

## Tests

```bash
python -m unittest discover -s tests -v
```

The unit suite injects a deterministic NLP boundary and checks the supported regex patterns, named-entity replacement, file processing, CLI failure status, and PDF output naming. CI runs these core checks without downloading the large language model; it is not a full smoke test of the spaCy model or PDF runtime.

## Privacy and compliance limits

The project name describes its learning goal; using this program does **not** establish GDPR/DSGVO compliance or guarantee anonymization.

- Regex and statistical NER can produce false positives and false negatives.
- Detected person and location text is replaced by value throughout the document. Identical text outside the detected context can therefore also be replaced.
- The supported patterns cover only a small subset of personal-data formats and do not cover the full DACH region.
- Replacing names and locations does not address re-identification through context or linked datasets.
- Extracted PDF text can omit scanned content, annotations, form fields, images, and layout-dependent meaning.
- Always review output manually and perform an appropriate legal, privacy, and risk assessment before processing real personal data.
- Test with synthetic data first; do not send sensitive documents to unapproved environments.
