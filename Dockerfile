FROM python:3.12-slim

ARG APPDIR=/app
RUN mkdir -p ${APPDIR}
WORKDIR $APPDIR

COPY requirements.txt $APPDIR
RUN pip install -r requirements.txt

COPY misskey_note_ingester.py $APPDIR

CMD ["python", "./misskey_note_ingester.py"]
