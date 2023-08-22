FROM python:3.10-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix="/install" --no-warn-script-location -r requirements.txt

FROM python:3.10-slim AS runner

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/cache/apt/lists.d

WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .

ENTRYPOINT ["python", "main.py"]
