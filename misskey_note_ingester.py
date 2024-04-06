import json
import os
import sys
import uuid

import boto3
from websocket import WebSocketApp


class MisskeyNoteIngester:
    """
    A class that ingests notes from Misskey API and sends them to an AWS Firehose stream.

    Args:
        misskey_api_token (str): The API token for accessing the Misskey API.
        misskey_api_endpoint (str): The endpoint URL for the Misskey API.
        aws_region (str): The AWS region where the Firehose stream is located.
        aws_firehose_stream_name (str): The name of the Firehose stream.

    Attributes:
        misskey_api_token (str): The API token for accessing the Misskey API.
        misskey_api_endpoint (str): The endpoint URL for the Misskey API.
        aws_region (str): The AWS region where the Firehose stream is located.
        firehose_client (boto3.client): The Firehose client for interacting with the Firehose service.
        firehose_stream (str): The name of the Firehose stream.

    """

    def __init__(
        self,
        misskey_api_token: str,
        misskey_api_endpoint: str,
        aws_region: str,
        aws_firehose_stream_name: str,
    ):
        self.misskey_api_token = misskey_api_token
        self.misskey_api_endpoint = f"{misskey_api_endpoint}?i={self.misskey_api_token}"
        self.aws_region = aws_region
        self.firehose_client = boto3.client("firehose", region_name=self.aws_region)
        self.firehose_stream = aws_firehose_stream_name

        self.is_debug_mode = os.environ.get("DEBUG", "false")

    def connect(self):
        """
        Connects to the Misskey API WebSocket and starts listening for messages.

        """
        self.ws = WebSocketApp(
            self.misskey_api_endpoint,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        try:
            self.ws.run_forever(ping_interval=30, reconnect=5)
        except KeyboardInterrupt:
            print("Keyboard Interrupt has been detected. Exit.")
            self.ws.close()

    def on_open(self, ws: WebSocketApp):
        """
        Event handler for the WebSocket on_open event.

        Args:
            ws (WebSocketApp): The WebSocketApp instance.

        """
        print("OnOpen event has been triggered.")

        # Connect to 'Local Timeline' channel
        data = {
            "type": "connect",
            "body": {"channel": "localTimeline", "id": str(uuid.uuid4())},
        }
        ws.send(json.dumps(data))

    def on_message(self, ws: WebSocketApp, message: str):
        """
        Event handler for the WebSocket on_message event.

        Args:
            ws (WebSocketApp): The WebSocketApp instance.
            message (str): The received message.

        """
        #print("OnMessage event has been triggered.")
        if self.is_debug_mode == "true":
            print(f"OnMessage: {message}")
            return

        self.firehose_client.put_record(
            DeliveryStreamName=self.firehose_stream, Record={"Data": message}
        )

    def on_error(self, ws: WebSocketApp, error):
        """
        Event handler for the WebSocket on_error event.

        Args:
            ws (WebSocketApp): The WebSocketApp instance.
            error: The error object.

        """
        print(f"OnError event has been triggered. Type: {type(error)}", error)
        print("Reconnecting...")
        self.connect()

    def on_close(self, ws: WebSocketApp, close_status_code, close_message):
        """
        Event handler for the WebSocket on_close event.

        Args:
            ws (WebSocketApp): The WebSocketApp instance.
            close_status_code (int): The status code of the close event.
            close_message (str): The close message.

        """
        print("OnClose event has been triggered.")
        print(f"StatusCode: {close_status_code}, Message: {close_message}")


def main():
    print("Starting Misskey Note Ingester.")

    misskey_token = os.environ.get("MISSKEY_TOKEN")
    misskey_endpoint = os.environ.get("MISSKEY_ENDPOINT")
    aws_region = os.environ.get("AWS_REGION")
    aws_firehose_stream_name = os.environ.get("AWS_FIREHOSE_STREAM")

    if misskey_token is None:
        print("MISSKEY_TOKEN is not set. exit.")
        sys.exit(-1)
    if misskey_endpoint is None:
        print("MISSKEY_ENDPOINT is not set. exit.")
        sys.exit(-1)
    if aws_region is None:
        print("AWS_REGION is not set. exit.")
        sys.exit(-1)
    if aws_firehose_stream_name is None:
        print("AWS_FIREHOSE_STREAM is not set. exit.")
        sys.exit(-1)

    print(f"MISSKEY_ENDPOINT:    {misskey_endpoint}")
    print(f"AWS_REGION:          {aws_region}")
    print(f"AWS_FIREHOSE_STREAM: {aws_firehose_stream_name}")

    app = MisskeyNoteIngester(
        misskey_token, misskey_endpoint, aws_region, aws_firehose_stream_name
    )
    app.connect()


if __name__ == "__main__":
    main()
