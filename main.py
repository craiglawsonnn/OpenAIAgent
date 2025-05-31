import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load tool definitions from tools.json
with open("tools.json", "r") as f:
    tools = json.load(f)

# Ask the user for input
user_input = input("You: ")

# Initial message list
messages = [
    {
        "role": "system",
        "content": (
            "You are a friendly customer service chatbot for an online store. "
            "Assist users with order issues, returns, refunds, tracking, and account updates. "
            "Use the tools provided to perform tasks when needed."
        )
    },
    {
        "role": "user",
        "content": user_input
    }
]

# Step 1: Get initial response and tool call (if needed)
response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

tool_calls = response.choices[0].message.tool_calls

# Step 2: Handle tool call if it exists
if tool_calls:
    tool_call = tool_calls[0]
    tool_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    # Simulated tool behavior
    def simulate_tool(name, args):
        if name == "get_order_status":
            return f"Order {args['order_id']} is on the way! Estimated delivery: June 6."
        elif name == "initiate_return":
            return f"A return has been initiated for order {args['order_id']} due to: '{args['reason']}'."
        elif name == "check_refund_status":
            return f"Refund {args['refund_id']} has been processed and should appear in your account within 3–5 days."
        elif name == "track_shipment":
            return f"Tracking number {args['tracking_number']} shows the package is in transit and expected tomorrow."
        elif name == "update_account_info":
            return f"Account info updated for customer {args['customer_id']} with new email/phone if provided."
        else:
            return f"(Simulated) Unknown tool: {name}"

    tool_result = simulate_tool(tool_name, args)

    # Step 3: Send tool result back to model
    followup = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            *messages,
            response.choices[0].message,
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": tool_result
            }
        ]
    )

    print("Bot:", followup.choices[0].message.content)

else:
    # No tool used, just reply
    print("Bot:", response.choices[0].message.content)
