import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY automatically

SYSTEM = """You are a practical assistant for professional handymen,
answering over WhatsApp. Rules:
- Give short, clear, step-by-step answers (under 1200 characters).
- Be specific: drill bit types, speeds, materials, tools.
- Always mention key safety points (PPE, hidden wires/pipes, dust).
- If the answer depends on something (wall type, wood type), ask ONE
  quick question or cover the main cases.
- If a job looks dangerous or needs a licensed pro (gas, mains
  electrical), say so.
- Plain text only, no markdown, light emoji use is fine."""

history = {}  # remembers each person's recent chat (resets on restart)

@app.post("/whatsapp")
def whatsapp():
    sender = request.form["From"]
    text = request.form.get("Body", "")

    msgs = history.setdefault(sender, [])
    msgs.append({"role": "user", "content": text})
    del msgs[:-10]  # keep last 10 messages only

    result = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=600,
        system=SYSTEM,
        messages=msgs,
    )
    answer = result.content[0].text
    msgs.append({"role": "assistant", "content": answer})

    reply = MessagingResponse()
    reply.message(answer[:1500])  # WhatsApp/Twilio length limit
    return str(reply)

@app.get("/")
def home():
    return "Handyman bot is alive!"
