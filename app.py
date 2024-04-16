from time import sleep
import os

import boto3
import requests

s3 = boto3.client("s3")
ASSEMBLY_AI_API_TOKEN = os.environ["ASSEMBLY_AI_API_TOKEN"]
ASSEMBLY_AI_ENDPOINT = "https://api.assemblyai.com/v2/transcript"
HEADERS = {"authorization": ASSEMBLY_AI_API_TOKEN}
SLEEP_INTERVAL = 3


class TranscriptionError(RuntimeError):
    """Raised when transcription fails."""


def submit_transcription_request(audio_url):
    payload = {"audio_url": audio_url}
    response = requests.post(ASSEMBLY_AI_ENDPOINT, json=payload, headers=HEADERS)
    return response.json()


def check_transcript_readiness(transcript_id):
    print(f"Checking transcription readiness for '{transcript_id}'...")
    polling_endpoint = f"{ASSEMBLY_AI_ENDPOINT}/{transcript_id}"
    while True:
        transcription_result = requests.get(polling_endpoint, headers=HEADERS).json()
        if transcription_result["status"] == "completed":
            break
        elif transcription_result["status"] == "error":
            raise TranscriptionError(f"Transcription failed: {transcription_result['error']}")
        else:
            sleep(SLEEP_INTERVAL)


def get_subtitle_file(transcript_id, file_format="srt"):
    if file_format not in ["srt", "vtt"]:
        raise ValueError("Invalid file format. Valid formats are 'srt' and 'vtt'.")
    print(f"Retrieving {file_format.upper()} file for '{transcript_id}'...")
    url = f"{ASSEMBLY_AI_ENDPOINT}/{transcript_id}/{file_format}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.text
    else:
        raise TranscriptionError(
            f"Failed to retrieve {file_format.upper()} file: {response.status_code} {response.reason}"
        )


def lambda_handler(event, context):
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    audio_url = f"https://{bucket_name}.s3.amazonaws.com/{key}"

    response = submit_transcription_request(audio_url)
    transcript_id = response["id"]
    check_transcript_readiness(transcript_id)
    srt_content = get_subtitle_file(transcript_id, "srt")

    s3.put_object(Bucket=bucket_name, Key=f"{transcript_id}.srt", Body=srt_content)
    return {"statusCode": 200, "body": "Transcription and download completed"}
