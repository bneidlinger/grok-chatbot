from flask import Flask, request, jsonify, render_template
import requests
from flask_socketio import SocketIO, emit
import eventlet
from transformers import pipeline

app = Flask(__name__, template_folder="templates", static_folder="static")
socketio = SocketIO(app, cors_allowed_origins="*")

# Load the local GPT-2 model
chatbot = pipeline("text-generation", model="gpt2")


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    ai_response = chatbot(user_input, max_length=50, num_return_sequences=1)[0]["generated_text"]
    return jsonify({"response": ai_response})


@socketio.on("message")
def handle_message(message):
    emit("response", {"type": "typing"}, broadcast=True)  # Send typing indicator
    eventlet.sleep(1.5)  # Simulate typing delay
    ai_response = chatbot(message, max_length=50, num_return_sequences=1)[0]["generated_text"]
    emit("response", {"type": "message", "text": ai_response})


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)