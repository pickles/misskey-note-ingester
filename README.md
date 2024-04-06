# Project Name
Misskey Note Ingester

## Description
Ingests notes from Misskey API and sends them to an AWS Firehose stream

## Installation
- git clone misskey-note-insgester.git
- docker build -t misskey-note-ingester:<tag> .

## Usage
docker run --rm \
  -e MISSKEY_TOKEN=<token> \
  -e MISSKEY_ENDPOINT=<endpoint> \
  -e AWS_REGION=<region> \
  -e AWS_FIREHOSE_STREAM=<stream_name> \
  -e AWS_ACCESS_KEY_ID=<access_key> \
  -e AWS_SECRET_ACCESS_KEY=<secret_key> \
  misskey-note-ingester:<tag>
