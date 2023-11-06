
# Assistant.py Script


# ======================[ IMPORTS AND INITIALIZATIONS ]======================#

import speech_recognition as sr
import torch
from TTS.api import TTS
import webbrowser
import openai
import pygame.mixer
from config import TamaKey

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v1.1").to(device)

# Initialize the mixer
pygame.mixer.init()

# Load the .wav files
Google = pygame.mixer.Sound('Wav Files/Google.wav')
Youtube = pygame.mixer.Sound('Wav Files/Youtube.wav')

# Configure your API key directly here if not using a separate config.
openai.api_key = TamaKey

# Initialize the recognizer and text-to-speech engine
recognizer = sr.Recognizer()

# Initialize a flag to check if the assistant is currently speaking
is_assistant_speaking = False

# Initialize a list to keep track of message logs
assistant_message_log = []

def save_response_to_file(response_text):
    with open("tama_responses.txt", "a") as file:
        file.write(response_text + "\n")

def process_openai_response(text):
    global is_assistant_speaking
    # Append user message to the assistant's log
    assistant_message_log.append({"role": "user", "content": text})
    
    # Add Tama's character role to the log
    assistant_message_log.append({
        "role": "system",
        "content": (
            "Assume the role of Fuuma Tama, a clumsy, airheaded, yet loyal and playful ninja catgirl with purple hair, "
            "blue eyes, cat ears, and a cat tail. You love cuddles, fluffy food, cosplay, and fighting. Always wear your "
            "unique outfit of a purple T-shirt, short skirt, and short white socks, complemented by hairpins "
            "and a scarf. Treat me as if I am your big brother. Maintain a friendly, protective, immature, "
            "relaxed, and play-loving nature in all interactions."
        )
    })
    
    # Check if there's enough messages for a proper conversation
    if len(assistant_message_log) >= 2:
        # Make an OpenAI API call
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=assistant_message_log,
            max_tokens=100,
            temperature=0.7
        )
        
        # Get the text response from the API call
        response_text = completion.choices[0].message['content']
        
        # Save the response to a text file
        save_response_to_file(response_text)
        
        # Add the response to the log
        assistant_message_log.append({"role": "assistant", "content": response_text})

        # Set the flag to True to indicate the assistant is speaking
        is_assistant_speaking = True

        # Speak the response
        tts.tts_to_file(text=response_text, file_path="TamaResponse.wav", speaker_wav="Voices\\Noelle\\Noelle_1.wav", language="en")
        TamaResponse = pygame.mixer.Sound('TamaResponse.wav')
        TamaResponse.play()

        # Wait for the TTS response to finish playing
        while pygame.mixer.get_busy():
            pass

        # Set the flag to False as the assistant has finished speaking
        is_assistant_speaking = False

def process_commands(command):
    if is_assistant_speaking:
        return  # Do nothing if the assistant is currently speaking

    if "open google" in command:
        Google.play()
        webbrowser.open("https://www.google.com")
    elif "open youtube" in command:
        Youtube.play()
        webbrowser.open("https://www.youtube.com")
    # ... include other commands here
    else:
        # If no commands match, process it as a conversation with OpenAI
        process_openai_response(command)

def listen_and_process_commands():
    if is_assistant_speaking:
        return  # Do nothing if the assistant is currently speaking

    with sr.Microphone() as source:
        print("Listening for commands...")
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio).lower()
        process_commands(command)
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")

# Main function
def main():
    while True:
        listen_and_process_commands()

if __name__ == "__main__":
    main()
