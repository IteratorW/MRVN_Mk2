FROM python:3.10-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix="/install" --no-warn-script-location -r requirements.txt

FROM python:3.10-slim AS runner

WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .

ENTRYPOINT ["/usr/bin/python", "main.py"]
