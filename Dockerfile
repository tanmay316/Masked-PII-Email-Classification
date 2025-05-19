FROM python:3.9-slim as builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev build-essential

WORKDIR /app
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

FROM python:3.9-slim
WORKDIR /app

# ✅ Set writable Hugging Face cache directory
ENV HF_HOME=/app/hf_cache

# ✅ Create the cache directory with proper permissions
RUN mkdir -p /app/hf_cache && chmod -R 777 /app/hf_cache

# ✅ Copy installed packages from builder
COPY --from=builder /usr/local /usr/local

# ✅ Copy your app code
COPY . .

# ✅ Download spaCy models
RUN python -m spacy download en_core_web_lg && \
    python -m spacy download de_core_news_md && \
    python -m spacy download es_core_news_md && \
    python -m spacy download fr_core_news_md && \
    python -m spacy download pt_core_news_md && \
    python -m spacy download nl_core_news_md && \
    python -m spacy download it_core_news_md

EXPOSE 7860
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "main:app"]
