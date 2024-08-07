from flask import Flask, render_template, jsonify, request
from kani import Kani, chat_in_terminal
from kani.engines.openai import OpenAIEngine
import gradio as gr
import openai
import asyncio
from kani import ChatMessage
from dotenv import load_dotenv
import os 
from flask_cors import CORS

load_dotenv()
my_key = os.getenv("OPENAI_API_KEY")
engine = OpenAIEngine(my_key, model="gpt-4")

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("test.html")

# @app.route("/api/send_message", methods=["POST"])
# def send_message():
#     data = request.json
#     transcript = data.get("transcript", "")
#     result = asyncio.run(cpAssistantModel(transcript))
#     return jsonify({"result": result})


async def cpAssistantModel(transcript):
    fewshot = [
        ChatMessage.system("You are helping the caregiver of a cerebral palsy patient understand \
            what the cerebral palsy patient is trying to say. You will typically receive under 3 words, \
            and the input maybe misspelt or incomplete; it might also be badly transcribed from audio.\
            Based on that input, you will try to understand the user's intention and confirm that with \
            the user by asking. If the user says no or 'n', that means your original suggestion is wrong, and \
            you will make another suggestion; keep doing this until the user says yes or 'y'. \
            If the user says yes or 'y', check if this intent is specific enough for the caregiver to take action; if not, keep following up \
            in the form more specific suggestions, and confirming with the user in the way as mentioned earlier. \
            At the end, rephrase the user's more specific intent in first-person as the message the user wants to tell the caregiver."),

        ChatMessage.user("walk"),
        ChatMessage.assistant("Do you need help walking to the door?"),
        ChatMessage.user("n"),
        ChatMessage.assistant("Do you want to go out for a walk?"),
        ChatMessage.user("y"),
        ChatMessage.assistant("Would you like to go out for a walk in the park?"),
        ChatMessage.user("n"),
        ChatMessage.assistant("Would you like to go out for a walk to the supermarket?"),
        ChatMessage.user("yes"),
        ChatMessage.assistant("I want to go out for a walk to the supermarket."),

        ChatMessage.user("bath"),
        ChatMessage.assistant("Do you need help taking a bath?"),
        ChatMessage.user("yeah"),
        ChatMessage.assistant("I need help taking a bath"),

        ChatMessage.user("drin"),
        ChatMessage.assistant("Do you want something to drink?"),
        ChatMessage.user("y"),
        ChatMessage.assistant("Would you like to drink some water?"),
        ChatMessage.user("n"),
        ChatMessage.assistant("Would you like to drink some orange juice?"),
        ChatMessage.user("n"),
        ChatMessage.assistant("Would you like to drink some milk?"),
        ChatMessage.user("ye"),
        ChatMessage.assistant("I want to drink some milk."),
    ]

    ai = Kani(engine, chat_history=fewshot)
    response = await ai.chat_round(transcript)
    return response

def process_audio(file_path):
    audio = open(file_path, "rb")
    openai.api_key = my_key
    transcript = openai.audio.transcriptions.create(model="whisper-1", file=audio, response_format='text')
    return transcript

@app.route("/api/main", methods=["POST"])
def main():
    data = request.json
    transcript = data.get("message", "")
    print(transcript)
    result = asyncio.run(cpAssistantModel(transcript))
    # elif user_choice == "2":
    #     audio_file_path = data.get("audio_file_path", "")
    #     transcript = process_audio(audio_file_path)
    #     print("transcript: ", transcript)
    #     asyncio.run(cpAssistantModel(transcript))
    # else:
    #     return jsonify({"error": "Invalid choice. Please enter '1' or '2'."})
    print(type(result))
    print(result.content)
    return jsonify({"result": result.content})
if __name__ == "__main__":
    app.run(debug=True, port=2450)