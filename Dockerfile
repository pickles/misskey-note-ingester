FROM python:3.12.2-slim

RUN apt-get update && apt-get install -y procps
RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt $WORKDIR
RUN pip install -r requirements.txt

COPY misskey_note_ingester.py $WORKDIR

CMD ["python", "./misskey_note_ingester.py"]
