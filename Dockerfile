FROM python:3.8-slim-buster

WORKDIR /bot
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

ENV IGNORED_MODULES=dummy
ENV SEARCH_DIRECTORIES=modules
CMD ["python3", "-m", "main"]