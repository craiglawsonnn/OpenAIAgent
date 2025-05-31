import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# System and user messages
messages = [
    {"role": "system", "content": "You are a helpful weather assistant."},
    {"role": "user", "content": "What's the weather like in Paris?"}
]

# Define the tool (function)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city to get weather for"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# Step 1: Let the model choose the tool
response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # You can also use "gpt-4o" if needed
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

# Step 2: Extract tool call
tool_calls = response.choices[0].message.tool_calls
if tool_calls:
    tool_call = tool_calls[0]
    tool_args = json.loads(tool_call.function.arguments)
    city = tool_args["city"]

    # Simulated tool result
    tool_result = f"The weather in {city} is sunny and 22°C."

    # Step 3: Send tool result back to model
    followup = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use the same model or a different one (this one is cheaper)
        messages=[
            *messages,
            response.choices[0].message,
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": "get_weather",
                "content": tool_result
            }
        ]
    )

    print("Assistant:", followup.choices[0].message.content)
else:
    # If no tool call was made
    print("Assistant:", response.choices[0].message.content)
