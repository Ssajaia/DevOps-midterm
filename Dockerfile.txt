
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

RUN chmod +x healthcheck.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD ./healthcheck.sh

CMD ["python", "main.py"]
