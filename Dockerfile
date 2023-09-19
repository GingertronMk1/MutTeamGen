FROM python:3.11.4-bullseye

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN apt update && \
    apt install -y \
        bsdmainutils \
        jq

RUN mypy ./*.py --install-types --non-interactive