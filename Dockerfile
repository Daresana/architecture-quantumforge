# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN --mount=type=secret,id=build_ca --mount=type=secret,id=build_ca_extra \
    if [ -f /run/secrets/build_ca ]; then \
        cat /run/secrets/build_ca /run/secrets/build_ca_extra > /tmp/build-ca.pem; \
        export PIP_CERT=/tmp/build-ca.pem; \
    fi; \
    pip install --no-cache-dir -r requirements.txt && rm -f /tmp/build-ca.pem

ENV PYTHONIOENCODING=utf-8
ENV PYTHONUTF8=1

COPY *.py ./
COPY knowledge_base ./knowledge_base
COPY index ./index
COPY fixtures ./fixtures

CMD ["python", "bot.py"]
