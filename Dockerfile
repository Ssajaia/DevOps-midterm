FROM alpine:latest

WORKDIR /app

RUN apk add --no-cache python3

COPY . .

RUN chmod +x healthcheck.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD ./healthcheck.sh

CMD ["python3", "main.py"]
