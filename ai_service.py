import os
from typing import List, Dict
from openai import OpenAI

# Initialize OpenAI client (Gemini also has a similar client, just swap if needed)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_sensor_insight(sensor_id: int, readings: List[Dict]) -> str:
    """
    Takes sensor readings and generates AI insights.
    Each reading dict = { "value": float, "unit": str, "timestamp": datetime }
    """

    # System prompt (controls the AI’s role and style)
    system_prompt = """
    You are an AI assistant specialized in analyzing IoT sensor data.
    Your task is to provide clear, concise insights about the readings.
    Focus on:
    - Trends over time
    - Anomalies or unusual values
    - Possible causes or real-world implications
    - Suggestions for monitoring or action
    """

    # User prompt (actual data and task)
    user_prompt = f"""
    Analyze the following readings from sensor ID {sensor_id}:

    {readings}

    Please summarize key insights in plain English.
    Format the response as a short JSON object with:
    - summary: high-level description
    - trends: patterns noticed
    - anomalies: any unusual values
    - recommendations: next steps
    """

    # Call GPT (chat style)
    response = client.chat.completions.create(
        model="gpt-4o-mini",   # or gemini-1.5-flash when using Gemini SDK
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
