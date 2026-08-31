import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from anonymizer import GDPRAnonymizer, default_output_path, main


class FakeNLP:
    def __init__(self, entities=()):
        self.entities = entities

    def __call__(self, _text):
        return SimpleNamespace(
            ents=[
                SimpleNamespace(text=text, label_=label)
                for text, label in self.entities
            ]
        )


class GDPRAnonymizerTests(unittest.TestCase):
    def test_pdf_default_output_is_plain_text(self):
        self.assertEqual(
            default_output_path("reports/input.pdf"), Path("redacted_input.txt")
        )

    def test_redacts_supported_structured_patterns(self):
        engine = GDPRAnonymizer(nlp=FakeNLP())

        result = engine.anonymize_text(
            "Mail: hans@example.test, IBAN: AT89 3704 0044 0532 0130, "
            "Telefon: +43 660 1234567"
        )

        self.assertEqual(
            result,
            "Mail: [EMAIL_REDACTED], IBAN: [IBAN_REDACTED], Telefon: [PHONE_REDACTED]",
        )

    def test_redacts_supported_person_and_location_entities(self):
        engine = GDPRAnonymizer(nlp=FakeNLP((("Hans Müller", "PER"), ("Wien", "LOC"))))

        result = engine.anonymize_text("Hans Müller lebt in Wien.")

        self.assertEqual(result, "[PERSON_GDPR] lebt in [LOCATION_GDPR].")

    def test_processes_plain_text_file(self):
        engine = GDPRAnonymizer(nlp=FakeNLP())
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "input.txt"
            output_path = Path(temp_dir) / "output.txt"
            input_path.write_text("Contact: hans@example.test", encoding="utf-8")

            engine.process_file(input_path, output_path)

            self.assertEqual(
                output_path.read_text(encoding="utf-8"),
                "Contact: [EMAIL_REDACTED]",
            )

    def test_missing_input_returns_failure(self):
        engine = GDPRAnonymizer(nlp=FakeNLP())

        self.assertFalse(engine.process_file("missing-input.txt", "output.txt"))

    def test_cli_returns_failure_when_processing_fails(self):
        with mock.patch("anonymizer.GDPRAnonymizer") as engine_type:
            engine_type.return_value.process_file.return_value = False

            exit_code = main(["input.txt"])

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
