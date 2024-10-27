# Build stage
FROM python:3.10-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
   build-essential \
   && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Final stage
FROM python:3.10-slim

# Create non-root user
RUN useradd -m -r -u 1000 siip

# Copy application files first
WORKDIR /app
COPY . /app/

# Copy wheels and install dependencies
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/*

# Install the package
RUN pip install -e .

# Switch to non-root user
USER siip

# Set environment variables with defaults
ENV DNS_PROVIDER=aws \
   REFRESH_INTERVAL=300

# Run the application
ENTRYPOINT ["si-ip"]