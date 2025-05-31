from flask import Flask, request, jsonify, render_template
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

app = Flask(__name__)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load tools once
with open("tools.json", "r") as f:
    tools = json.load(f)

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
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a friendly customer service chatbot for an online store. "
                "Assist users with order issues, returns, refunds, tracking, and account updates. "
                "Use tools if needed."
            )
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    tool_calls = response.choices[0].message.tool_calls

    if tool_calls:
        tool_call = tool_calls[0]
        tool_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        tool_result = simulate_tool(tool_name, args)

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

        return jsonify({"reply": followup.choices[0].message.content})

    return jsonify({"reply": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(debug=True)
