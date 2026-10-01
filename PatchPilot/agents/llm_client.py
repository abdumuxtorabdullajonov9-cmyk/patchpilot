import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ["NEBIUS_API_KEY"],
)

MODEL_NANO = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"
MODEL_ULTRA = "nvidia/Nemotron-3-Ultra-550b-a55b"