import os
import boto3
from dotenv import load_dotenv


# Load .env
load_dotenv()


# Read configuration
api_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
region = os.getenv("AWS_REGION", "us-east-1")


if not api_key:
    raise ValueError(
        "AWS_BEARER_TOKEN_BEDROCK is missing from .env"
    )


# Make the Bedrock API key available to Boto3
os.environ["AWS_BEARER_TOKEN_BEDROCK"] = api_key


# Create Bedrock Runtime client
client = boto3.client(
    service_name="bedrock-runtime",
    region_name=region
)


# Amazon Nova model
model_id = "amazon.nova-micro-v1:0"


# Test prompt
messages = [
    {
        "role": "user",
        "content": [
            {
                "text": (
                    "Explain in one sentence why an employee "
                    "might be assigned to a morning shift."
                )
            }
        ]
    }
]


# Call Nova
response = client.converse(
    modelId=model_id,
    messages=messages,
    inferenceConfig={
        "maxTokens": 200,
        "temperature": 0.3
    }
)


# Extract response
answer = response[
    "output"
]["message"]["content"][0]["text"]


print("\n===== NOVA TEST =====")
print(answer)
print("=====================\n")