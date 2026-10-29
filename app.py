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
- Reply in the same language the handyman writes in.
- Plain text only, no markdown, light emoji use is fine."""

history = {}  # remembers each person's recent chat (resets on restart)


@app.post("/whatsapp")
def whatsapp():
    sender = request.form.get("From", "unknown")
    text = request.form.get("Body", "").strip()

    reply = MessagingResponse()

    if not text:
        reply.message("Please send me a text question about your job. 🔧")
        return str(reply)

    msgs = history.setdefault(sender, [])
    msgs.append({"role": "user", "content": text})
    del msgs[:-10]  # keep last 10 messages only
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)  # history must start with a user message

    try:
        result = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=2000,
            system=SYSTEM,
            messages=msgs,
        )
        # Pick out only the text parts (the reply can also contain "thinking" parts)
        answer = "".join(
            block.text for block in result.content if block.type == "text"
        ).strip()
        if not answer:
            answer = "Sorry, I could not come up with an answer. Please ask again."
        msgs.append({"role": "assistant", "content": answer})
    except Exception as e:
        print("Error talking to Claude:", repr(e))
        msgs.pop()  # remove the question that failed
        answer = "Sorry, I had a problem answering. Please try again in a minute."

    reply.message(answer[:1500])  # keep within WhatsApp/Twilio length limit
    return str(reply)


@app.get("/")
def home():
    return "Handyman bot is alive!"
