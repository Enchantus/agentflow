FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# System deps (optional): add build tools if you later compile extras
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy and install
COPY pyproject.toml /app/
RUN pip install --no-cache-dir uvicorn fastapi

COPY src /app/agentflow
COPY agentflow.py /app/agentflow.py

EXPOSE 8080
CMD ["python", "agentflow.py", "--serve", "--host", "0.0.0.0", "--port", "8080"]
