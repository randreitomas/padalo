FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY packages/agent ./packages/agent
COPY packages/forecasting ./packages/forecasting
COPY data ./data
COPY apps/api/requirements.txt ./apps/api/requirements.txt
RUN pip install --no-cache-dir -r apps/api/requirements.txt

WORKDIR /app
COPY apps/api .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
