import os
from pathlib import Path
from sarvamai import SarvamAI

# Load .env file into environment if present
env_path = Path(__file__).parent / ".env"
if env_path.is_file():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = val

api_key = os.environ.get("SARVAM_API_KEY")
if not api_key:
    raise ValueError("SARVAM_API_KEY environment variable is not set. Please add it to your .env file.")

client = SarvamAI(api_subscription_key=api_key)

response = client.chat.completions(
    model="sarvam-105b-conversations",
    messages=[
        {"role": "user", "content": "Hello! Introduce yourself in one sentence."}
    ],
)

print(response.choices[0].message.content)

