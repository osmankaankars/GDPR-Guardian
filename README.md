# GDPR Guardian 🛡️

> **An automated Privacy Engineering tool designed for the DACH region to detect and anonymize Personal Identifiable Information (PII) in German texts.**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Compliance](https://img.shields.io/badge/Compliance-GDPR%2FDSGVO-orange)
![NLP](https://img.shields.io/badge/AI-Spacy_German_Model-green)

## 📖 Overview
In the era of strict data privacy regulations (**GDPR / DSGVO**), automated data minimization is essential.

**GDPR Guardian** is a Python-based utility that leverages **Natural Language Processing (NLP)** and region-specific regex patterns to sanitize documents before they leave secure environments.  
It is specifically engineered to handle **German language nuances** and **Austrian/German formats**.

## ✨ Key Features
* **🇦🇹 Region-Specific Detection:** Accurate identification of Austrian IBANs (`AT...`) and Phone Numbers (`+43`).
* **🧠 AI-Powered Named Entity Recognition:** Uses Spacy's `de_core_news_sm` model to detect German Names and Locations contextually.
* **📄 Multi-Format Support:** Processes both plain text (`.txt`) and PDF documents (`.pdf`).
* **🔒 Privacy by Design:** Implements pseudonymization placeholders (e.g., `[PERSON_GDPR]`) to maintain document structure while removing sensitive data.

## ⚙️ Installation

1. **Clone the repository:**
```bash
git clone https://github.com/osmankaankars/GDPR-Guardian.git
cd GDPR-Guardian
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Download the German Language Model:**
```bash
python -m spacy download de_core_news_sm
```

## 🚀 Usage
Run the tool via command line by passing the target file:

```bash
python anonymizer.py kunde_wien.txt
```

### Example Input:
```
Client: Hans Müller, Location: Wien, IBAN: AT89 3704 0044 0532 0130
```

### Example Output:
```
Client: [PERSON_GDPR], Location: [LOCATION_GDPR], IBAN: [IBAN_REDACTED]
```

## 👨‍💻 Author
**Osman Kaan Kars**  
Cybersecurity Engineer | Privacy Engineering Enthusiast  

Connect with me on LinkedIn for specialized DACH region security projects.