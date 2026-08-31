import re
import sys
from pathlib import Path

from termcolor import colored


def default_output_path(input_path):
    """Choose a text output path; PDF extraction does not produce a new PDF."""
    input_path = Path(input_path)
    suffix = ".txt" if input_path.suffix.lower() == ".pdf" else input_path.suffix
    return Path(f"redacted_{input_path.stem}{suffix}")


class GDPRAnonymizer:
    """
    A small redaction helper for a limited set of structured patterns and
    German-language named entities.
    """

    def __init__(self, nlp=None):
        if nlp is None:
            import spacy

            print(colored("[*] Initializing GDPR Guardian...", "cyan"))
            print(colored("[*] Loading NLP Model: de_core_news_sm (German)...", "cyan"))
            try:
                nlp = spacy.load("de_core_news_sm")
            except OSError as error:
                raise RuntimeError(
                    "German model not found. Run: python -m spacy download de_core_news_sm"
                ) from error
        self.nlp = nlp

        # --- REGEX PATTERNS SUPPORTED BY THIS PROTOTYPE ---

        # IBAN (Austria): Starts with AT, followed by 18 digits (formatted or unformatted)
        self.iban_pattern = r"AT\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}"

        # Phone Numbers (Austria/Germany): Matches +43, +49 or 0 pre-fix
        self.phone_pattern = r"(\+43|\+49|0)\s?(\d{1,4})\s?(\d+[\d\s-]*)"

        # Email Addresses (Standard RFC 5322 regex adaptation)
        self.email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    def anonymize_text(self, text):
        """
        Scans the input text for PII and replaces them with [REDACTED] placeholders.
        """

        # 1. Regex-Based Redaction (Structured Data)
        text = re.sub(self.iban_pattern, "[IBAN_REDACTED]", text)
        text = re.sub(self.phone_pattern, "[PHONE_REDACTED]", text)
        text = re.sub(self.email_pattern, "[EMAIL_REDACTED]", text)

        # 2. NLP-Based Redaction (Unstructured Data: Names, Locations)
        doc = self.nlp(text)

        # We use a placeholder approach to preserve text structure.
        # Iterating entities and replacing exact matches.
        anonymized_text = text

        for ent in doc.ents:
            if ent.label_ == "PER":  # Person Names
                anonymized_text = anonymized_text.replace(ent.text, "[PERSON_GDPR]")
            elif ent.label_ == "LOC":  # Locations (Cities, Addresses)
                anonymized_text = anonymized_text.replace(ent.text, "[LOCATION_GDPR]")

        return anonymized_text

    def process_file(self, input_path, output_path):
        """
        Reads a file (TXT or PDF), applies anonymization, and saves the output.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        if not input_path.is_file():
            print(colored(f"[-] Error: File '{input_path}' not found.", "red"))
            return False

        print(colored(f"[*] Processing Document: {input_path}", "yellow"))

        try:
            # Handle PDF Files
            if input_path.suffix.lower() == ".pdf":
                import fitz  # PyMuPDF

                with fitz.open(input_path) as doc:
                    full_text = "".join(page.get_text() for page in doc)
            # Handle Text Files
            else:
                with open(input_path, "r", encoding="utf-8") as f:
                    full_text = f.read()

            # Execute Anonymization
            clean_text = self.anonymize_text(full_text)

            # Save Result
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(clean_text)

            print(
                colored(f"[+] Success! Anonymized file saved: {output_path}", "green")
            )

            # Statistics
            original_len = len(full_text)
            clean_len = len(clean_text)
            print(f"    > Original Size: {original_len} chars")
            print(f"    > Redacted Size: {clean_len} chars")
            print("-" * 50)
            return True

        except (OSError, UnicodeError, RuntimeError, ValueError) as error:
            print(colored(f"[-] Critical Error: {error!s}", "red"))
            return False


def main(argv=None):
    """Run the command-line interface and return a process exit code."""
    argv = sys.argv[1:] if argv is None else argv
    print(
        colored(
            "=== GDPR GUARDIAN | Privacy Engineering Tool ===", "white", attrs=["bold"]
        )
    )

    if not argv:
        print(colored("Usage: python anonymizer.py <path_to_file>", "yellow"))
        return 2

    target_file = argv[0]
    output_filename = default_output_path(target_file)
    try:
        engine = GDPRAnonymizer()
    except RuntimeError as error:
        print(colored(f"[-] {error}", "red"))
        return 1

    return 0 if engine.process_file(target_file, output_filename) else 1


if __name__ == "__main__":
    sys.exit(main())
