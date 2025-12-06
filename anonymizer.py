import spacy
import re
import os
import sys
import fitz  # PyMuPDF
from termcolor import colored

class GDPRAnonymizer:
    """
    A privacy engineering class designed to detect and redact Personal Identifiable Information (PII)
    specifically tailored for the DACH region (Germany, Austria, Switzerland).
    """

    def __init__(self):
        print(colored("[*] Initializing GDPR Guardian...", "cyan"))
        print(colored("[*] Loading NLP Model: de_core_news_sm (German)...", "cyan"))
        
        try:
            self.nlp = spacy.load("de_core_news_sm")
        except OSError:
            print(colored("[-] Model not found. Please run: python -m spacy download de_core_news_sm", "red"))
            sys.exit(1)
        
        # --- REGEX PATTERNS FOR DACH REGION ---
        
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
            elif ent.label_ == "LOC": # Locations (Cities, Addresses)
                anonymized_text = anonymized_text.replace(ent.text, "[LOCATION_GDPR]")
                
        return anonymized_text

    def process_file(self, input_path, output_path):
        """
        Reads a file (TXT or PDF), applies anonymization, and saves the output.
        """
        if not os.path.exists(input_path):
            print(colored(f"[-] Error: File '{input_path}' not found.", "red"))
            return

        print(colored(f"[*] Processing Document: {input_path}", "yellow"))
        
        try:
            # Handle PDF Files
            if input_path.lower().endswith(".pdf"):
                doc = fitz.open(input_path)
                full_text = ""
                for page in doc:
                    full_text += page.get_text()
            # Handle Text Files
            else:
                with open(input_path, "r", encoding="utf-8") as f:
                    full_text = f.read()

            # Execute Anonymization
            clean_text = self.anonymize_text(full_text)
            
            # Save Result
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(clean_text)
                
            print(colored(f"[+] Success! Anonymized file saved: {output_path}", "green"))
            
            # Statistics
            original_len = len(full_text)
            clean_len = len(clean_text)
            print(f"    > Original Size: {original_len} chars")
            print(f"    > Redacted Size: {clean_len} chars")
            print("-" * 50)

        except Exception as e:
            print(colored(f"[-] Critical Error: {str(e)}", "red"))

if __name__ == "__main__":
    print(colored("=== GDPR GUARDIAN | Privacy Engineering Tool ===", "white", attrs=['bold']))
    
    # Simple CLI Argument Parser
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        output_filename = f"redacted_{os.path.basename(target_file)}"
        
        engine = GDPRAnonymizer()
        engine.process_file(target_file, output_filename)
    else:
        print(colored("Usage: python anonymizer.py <path_to_file>", "yellow"))
