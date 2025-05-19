# 2) Imports
import pandas as pd
import re
from presidio_analyzer import (
    RecognizerRegistry,
    AnalyzerEngine,
    PatternRecognizer,
    Pattern,
)
from presidio_analyzer.predefined_recognizers import (
    EmailRecognizer,
    PhoneRecognizer,
    DateRecognizer,
    CreditCardRecognizer,
    SpacyRecognizer,
)
from presidio_analyzer.context_aware_enhancers import LemmaContextAwareEnhancer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer.nlp_engine import NlpEngineProvider


# 3) Enhanced text preprocessing
def clean_text(text):
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove special characters except basic punctuation
    text = re.sub(r"[^a-zA-Z0-9\s.,!?]", "", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


# 4) Build spaCy NLP engine for all target languages (added nl/it)
nlp_conf = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": code, "model_name": model}
        for code, model in [
            ("en", "en_core_web_lg"),
            ("de", "de_core_news_md"),
            ("es", "es_core_news_md"),
            ("fr", "fr_core_news_md"),
            ("pt", "pt_core_news_md"),
            ("nl", "nl_core_news_md"),
            ("it", "it_core_news_md"),
        ]
    ],
}
nlp_engine = NlpEngineProvider(nlp_configuration=nlp_conf).create_engine()

# 4) Create registry and register context-aware enhancer
registry = RecognizerRegistry()
# Explicitly set supported languages
registry.supported_languages = ["en", "de", "es", "fr", "pt", "nl", "it"]
# Instantiate LemmaContextAwareEnhancer with sensible defaults
enhancer = LemmaContextAwareEnhancer(
    context_similarity_factor=0.35,
    min_score_with_context_similarity=0.4,
    context_prefix_count=3,
    context_suffix_count=3,
)
# 5) Register built-in and custom recognizers with language-specific context cues
language_contexts = {
    "en": {
        "person": ["name", "called", "i am", "my name is"],
        "email": ["email", "e-mail", "mail address"],
        "phone": ["phone", "tel", "mobile number"],
        "date": ["born", "dob", "birthdate", "birth date"],
        "card": ["card", "credit", "debit", "cvv", "expiry"],
    },
    "de": {
        "person": ["name", "heiße", "ich bin", "mein name ist", "herr", "frau"],
        "email": ["e-mail", "mail", "email-adresse"],
        "phone": ["telefon", "handy", "telefonnummer"],
        "date": ["geburtsdatum", "geburtstag", "datum"],
        "card": ["karte", "kreditkarte", "debitkarte", "ablaufdatum", "cvv"],
    },
    "es": {
        "person": ["nombre", "me llamo", "soy", "mi nombre es", "señor", "señora"],
        "email": ["correo", "electrónico", "correo electrónico"],
        "phone": ["teléfono", "móvil", "número de teléfono"],
        "date": ["nacimiento", "fecha de nacimiento"],
        "card": ["tarjeta", "crédito", "débito", "cvv", "fecha de vencimiento"],
    },
    "fr": {
        "person": [
            "nom",
            "je suis",
            "je m’appelle",
            "mon nom est",
            "monsieur",
            "madame",
        ],
        "email": ["courriel", "email", "adresse électronique"],
        "phone": ["téléphone", "portable", "numéro de téléphone"],
        "date": ["naissance", "date de naissance"],
        "card": ["carte", "crédit", "débit", "cvv", "date d’expiration"],
    },
    "pt": {
        "person": ["nome", "me chamo", "sou", "meu nome é"],
        "email": ["email", "correio", "endereço de email"],
        "phone": ["telefone", "celular", "número de telefone"],
        "date": ["nascimento", "data de nascimento"],
        "card": ["cartão", "crédito", "débito", "cvv", "validade"],
    },
    "it": {
        "person": ["nome", "mi chiamo", "sono", "il mio nome è", "signor", "signora"],
        "email": ["email", "indirizzo email", "posta elettronica"],
        "phone": ["telefono", "numero di telefono", "cellulare"],
        "date": ["nascita", "data di nascita", "compleanno"],
        "card": [
            "carta",
            "carta di credito",
            "carta di debito",
            "numero carta",
            "cvv",
            "scadenza",
        ],
    },
    "nl": {
        "person": [
            "naam",
            "ik ben",
            "mijn naam is",
            "voornaam",
            "achternaam",
            "dhr",
            "mevrouw",
        ],
        "email": ["e-mail", "e-mailadres", "emailadres"],
        "phone": ["telefoon", "telefoonnummer", "mobiel nummer", "mobiele telefoon"],
        "date": ["geboortedatum", "verjaardag", "datum van geboorte"],
        "card": [
            "kaart",
            "creditcard",
            "debetkaart",
            "pinpas",
            "bankkaart",
            "kaartnummer",
            "cvv",
            "vervaldatum",
        ],
    },
}

for lang, ctx in language_contexts.items():
    # Detect PERSON via spaCy NER, boosted by context words
    registry.add_recognizer(
        SpacyRecognizer(
            supported_language=lang,
            supported_entities=["PERSON"],
            context=ctx["person"],
        )
    )
    # Email, Phone, Date, CreditCard
    registry.add_recognizer(
        EmailRecognizer(supported_language=lang, context=ctx["email"])
    )
    registry.add_recognizer(
        PhoneRecognizer(supported_language=lang, context=ctx["phone"])
    )
    registry.add_recognizer(
        DateRecognizer(supported_language=lang, context=ctx["date"])
    )
    registry.add_recognizer(
        CreditCardRecognizer(supported_language=lang, context=ctx["card"])
    )

# Custom regex recognizers for Aadhar, CVV, Expiry with context
registry.add_recognizer(
    PatternRecognizer(
        supported_entity="IN_AADHAAR",
        patterns=[Pattern("aadhar", r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", 0.8)],
        context=["aadhar", "uidai"],
    )
)
registry.add_recognizer(
    PatternRecognizer(
        supported_entity="CVV_NO",
        patterns=[Pattern("cvv", r"\b\d{3,4}\b", 0.7)],
        context=["cvv", "cvc", "security code"],
    )
)
registry.add_recognizer(
    PatternRecognizer(
        supported_entity="EXPIRY_NO",
        patterns=[Pattern("expiry", r"\b(0[1-9]|1[0-2])/(?:\d{2}|\d{4})\b", 0.7)],
        context=["expiry", "valid thru", "valide"],
    )
)

# 6) Instantiate the AnalyzerEngine with our enhancer and a lower base threshold
analyzer = AnalyzerEngine(
    registry=registry,
    nlp_engine=nlp_engine,
    supported_languages=["en", "de", "es", "fr", "pt", "nl", "it"],
    context_aware_enhancer=enhancer,
    default_score_threshold=0.3,
)
anonymizer = AnonymizerEngine()

# 7) Entity → mask token map
pres_map = {
    "PERSON": "[full_name]",
    "EMAIL_ADDRESS": "[email]",
    "PHONE_NUMBER": "[phone_number]",
    "DATE_TIME": "[dob]",
    "IN_AADHAAR": "[aadhar_num]",
    "CREDIT_CARD": "[credit_debit_no]",
    "CVV_NO": "[cvv_no]",
    "EXPIRY_NO": "[expiry_no]",
}


# 8) Merge overlapping spans
def merge_spans(spans):
    spans = sorted(spans, key=lambda x: x.start)
    merged = []
    for s in spans:
        if merged and s.start <= merged[-1].end:
            # keep the longest span
            if (s.end - s.start) > (merged[-1].end - merged[-1].start):
                merged[-1] = s
        else:
            merged.append(s)
    return merged


# 9) Corrected mask_pii function
def mask_pii(text: str):
    # 1) Detect PII across all languages
    detections = []
    for lang in ["en", "de", "es", "fr", "pt", "nl", "it"]:
        detections += analyzer.analyze(
            text=text,
            language=lang,
            entities=list(pres_map.keys()),
            score_threshold=0.3,
        )

    # 2) Merge overlapping detections
    spans = merge_spans(detections)

    # 3) Build operators dict using OperatorConfig
    operators = {
        ent: OperatorConfig("replace", {"new_value": tok})
        for ent, tok in pres_map.items()
    }

    # 4) Apply anonymization
    result = anonymizer.anonymize(
        text=text,
        analyzer_results=spans,
        operators={
            ent: OperatorConfig("replace", {"new_value": tok})
            for ent, tok in pres_map.items()
        },
    )

    # 5) Extract masked text and the list of original entities
    masked_text = result.text
    entities = []
    for s in spans:
        token = pres_map[s.entity_type]
        entities.append(
            {
                "position": [s.start, s.end],
                "classification": token.strip("[]"),
                "entity": text[s.start : s.end],
            }
        )

    return masked_text, entities
