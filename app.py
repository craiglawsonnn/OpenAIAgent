from flask import Flask, request, jsonify, render_template
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import sqlite3
from db import init_db
init_db()


chat_sessions = {}  # temporary memory keyed by IP or static ID

app = Flask(__name__)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load tools once
with open("tools.json", "r") as f:
    tools = json.load(f)

# Simulated tool behavior
def simulate_tool(name, args):
    if name == "get_order_status":
        conn = sqlite3.connect("support.db")
        cur = conn.cursor()
        cur.execute("SELECT status, delivery_date FROM orders WHERE id = ?", (args['order_id'],))
        row = cur.fetchone()
        conn.close()

        if row:
            return (
                f"Order {args['order_id']} is currently in the {row[0]} stage "
                f"and is estimated to be delivered on {row[1]}. If you have any further questions or need assistance, feel free to ask!"
            )
        else:
            return (
                f"I'm sorry, I couldn't find an order with ID {args['order_id']}. "
                f"Please double-check the number or contact a support agent for more help."
            )
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
def summarize_messages(message_history):
    # Convert any objects into serializable format
    simplified_history = []
    for msg in message_history:
        if hasattr(msg, "role") and hasattr(msg, "content"):
            simplified_history.append({
                "role": msg.role,
                "content": msg.content
            })
        elif isinstance(msg, dict):
            simplified_history.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

    summarization_prompt = [
        {
            "role": "system",
            "content": "You are a summarization engine that turns conversations into compact summaries of important info only."
        },
        {
            "role": "user",
            "content": f"Summarize this conversation:\n\n{json.dumps(simplified_history, indent=2)}"
        }
    ]
    
    result = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=summarization_prompt
    )
    
    return result.choices[0].message.content


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    session_id = "demo_user"  # for now; you can later use IP or auth info

    # Initialize session memory
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {
            "messages": [],
            "summary": None
        }

    session = chat_sessions[session_id]

    # Add user's message
    session["messages"].append({"role": "user", "content": user_input})

    # Check if we need to summarize (every 6 turns)
    if len(session["messages"]) >= 6:
        session["summary"] = summarize_messages(session["messages"])
        session["messages"] = []  # reset message history

    # Build full prompt: summary (if any) + last few messages
    full_prompt = []

    if session["summary"]:
        full_prompt.append({
            "role": "system",
            "content": f"Summary of previous conversation: {session['summary']}"
        })

    full_prompt.extend(session["messages"])

    # Prepend system message with role instructions
    full_prompt.insert(0, {
        "role": "system",
        "content": "You are a helpful customer support agent."
    })

    # Generate response
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=full_prompt,
        tools=tools,
        tool_choice="auto"
    )

    tool_calls = response.choices[0].message.tool_calls

    if tool_calls:
        tool_call = tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        tool_result = simulate_tool(tool_call.function.name, args)

        # Add assistant's tool-calling message
        session["messages"].append(response.choices[0].message)

        # Add tool reply
        session["messages"].append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": tool_result
        })

        # Send final follow-up message
        final_response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                *full_prompt,
                response.choices[0].message,
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": tool_result
                }
            ]
        )

        session["messages"].append({"role": "assistant", "content": final_response.choices[0].message.content})
        return jsonify({"reply": final_response.choices[0].message.content})

    # If no tool call, just respond
    bot_reply = response.choices[0].message.content
    session["messages"].append({"role": "assistant", "content": bot_reply})
    return jsonify({"reply": bot_reply})


if __name__ == "__main__":
    app.run(debug=True)
