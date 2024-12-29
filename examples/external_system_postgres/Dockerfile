FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY app/ /app

# Set PYTHONPATH environment variable
ENV PYTHONPATH="/app"

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
