# 🛡️ PII Email Classification (Multilingual)

A Flask-based web API that detects and masks Personally Identifiable Information (PII) from multilingual email text and classifies the intent of the email using a fine-tuned XLM-Roberta model.

Hosted on: [HF Spaces](https://huggingface.co/spaces/tms43/PII_email_classification)

---

## 📌 Problem Statement

Build a multilingual system to:
1. **Mask PII** from emails (e.g., names, emails, phone numbers, Aadhar, etc.)
2. **Classify** emails into predefined categories such as Request, Complaint, etc.

---

## 🚀 Features

- ✅ PII detection using [Microsoft Presidio](https://github.com/microsoft/presidio)
- ✅ spaCy NER models for **7 languages** (en, de, es, fr, pt, nl, it)
- ✅ Custom regex recognizers (Aadhar, CVV, expiry)
- ✅ Fine-tuned [XLM-Roberta](https://huggingface.co/tms43/email_classifier_XLMRoberta) for email classification
- ✅ REST API with `/classify` endpoint
- ✅ API endpoint: https://tms43-PII-email-classification.hf.space/classify
- ✅ Dockerized and deployed on **Hugging Face Spaces**

---

## ⚙️ System Architecture

User Email Input
│
▼
[Mask PII]
(Presidio + spaCy + Regex)
│
▼
[Masked Email]
│
▼
[XLM-R Classifier]
│
▼
Category Output


---


### 🛠️ Setup (Local)
1. Clone the repo:
```
git clone https://github.com/tanmay316/PII_email_classification.git
cd PII_email_classification
```
2. Build & run with Docker:
```
docker build -t pii-app .
docker run -p 7860:7860 pii-app
```
### 🧪 API Usage
Endpoint:
```
POST [/classify](https://tms43-PII-email-classification.hf.space/classify)
```
Payload:
```
{
  "input_email_body": "..."
}
```
Response:
```
{
  "masked_email": "...",
  "list_of_masked_entities": [...],
  "category_of_the_email": "..."
}
```




