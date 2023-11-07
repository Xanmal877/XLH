# ======================[ IMPORTS AND INITIALIZATIONS ]====================== #

import speech_recognition as sr
import torch
from TTS.api import TTS
import openai
import pygame.mixer
from config import TamaKey
import asyncio
from Tasks.SmartHome import process_smart_home_command, SMART_HOME_ACTIONS
from Tasks.Websites import open_website, COMMAND_URLS

# ======================[ GLOBAL VARIABLES AND CONSTANTS ]=================== #

WAKE_WORDS = ["hey tama", "ok tama"]  # Define your wake words here

# TTS and speech recognition setup
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v1.1").to(device)
recognizer = sr.Recognizer()
pygame.mixer.init()
openai.api_key = TamaKey

# Flags and logs
is_assistant_speaking = False
# Initialize a list to keep track of message logs
assistant_message_log = []

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


# ======================[ UTILITY FUNCTIONS ]=============================== #

def save_response_to_file(response_text):
    with open("tama_responses.txt", "a") as file:
        file.write(response_text + "\n")

def process_openai_response(text):
    global is_assistant_speaking
    # Append user message to the assistant's log
    assistant_message_log.append({"role": "user", "content": text})
    
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

# ======================[ WAKE WORD DETECTION ]============================= #

async def listen_for_wake_word(recognizer, source):
    print("Listening for wake word...")
    audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        return any(wake_word in command for wake_word in WAKE_WORDS)
    except sr.UnknownValueError:
        return False
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return False

# ======================[ COMMAND PROCESSING ]============================== #

async def process_commands():
    global is_assistant_speaking

    if is_assistant_speaking:
        return  # Do nothing if the assistant is currently speaking

    # Start by capturing a spoken command
    with sr.Microphone() as source:
        print("Listening for commands...")
        audio = recognizer.listen(source)
    
    try:
        # Attempt to recognize the command through speech
        command = recognizer.recognize_google(audio).lower()

    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return

    # After capturing the command, proceed to process it
    # Check if the command relates to website operations
    if any(keyword in command for keyword in COMMAND_URLS):
        await open_website(command)
    # Check if the command relates to smart home control
    elif any(phrase in command for phrase in SMART_HOME_ACTIONS):
        await process_smart_home_command(command)
    else:
        # If the command is not related to websites or smart home, pass it to OpenAI's API
        return

# ======================[ MAIN PROCESSING LOOP ]============================ #

async def listen_and_process_commands():
    global is_assistant_speaking

    with sr.Microphone() as source:
        while True:  # Keep the program running
            if await listen_for_wake_word(recognizer, source):
                # Play a sound, speak a message, or print a message to acknowledge the wake word
                print("I'm here! What can I do for you?")
                # Optionally play a response sound or use TTS to audibly respond

                # Wait for a short moment before listening for a command
                await asyncio.sleep(1)

                # Now listen for an actual command
                await process_commands()

# ======================[ MAIN ENTRY POINT ]================================ #

# Main coroutine that starts the listening process
async def main():
    while True:
        await process_commands()

# Start the main loop
if __name__ == "__main__":
    asyncio.run(main())

