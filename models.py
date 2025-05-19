from transformers import AutoTokenizer, XLMRobertaForSequenceClassification

MODEL_ID = "tms43/email_classifier_XLMRoberta"

# Option A: direct hub load
model = XLMRobertaForSequenceClassification.from_pretrained(MODEL_ID)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

def classify_text(text: str) -> str:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    logits = model(**inputs).logits
    pred_id = logits.argmax(dim=1).item()
    return model.config.id2label[pred_id]







# Option B: local load

# from transformers import AutoTokenizer, XLMRobertaForSequenceClassification

# model = XLMRobertaForSequenceClassification.from_pretrained("email_classifier")
# tokenizer = AutoTokenizer.from_pretrained("email_classifier")


# def classify_text(text: str) -> str:
#     inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
#     logits = model(**inputs).logits
#     pred_id = logits.argmax(dim=1).item()
#     return model.config.id2label[pred_id]
