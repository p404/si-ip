# Build 
FROM python:3.10-slim as builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
   build-essential \
   && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Runtime
FROM python:3.10-slim
LABEL org.opencontainers.image.source="https://github.com/p404/si-ip"
LABEL org.opencontainers.image.description="SI-IP Is a A Dynamic DNS updater built on top of multiple DNS Providers e.g. AWS Route 53."
LABEL org.opencontainers.image.licenses="MIT"

RUN useradd -m -r -u 1000 siip
WORKDIR /app
COPY . /app/

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/*
RUN pip install -e .

USER siip
ENV DNS_PROVIDER=aws \
   REFRESH_INTERVAL=300

ENTRYPOINT ["si-ip"]