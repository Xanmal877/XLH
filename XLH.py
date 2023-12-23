# ======================[ IMPORTS AND INITIALIZATIONS ]====================== #

import os
import keyboard
import asyncio
import pygame.mixer
import openai
import torch
import torchaudio
import speech_recognition as sr
from config import OpenAIKey
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from TTS.api import TTS
from Tasks.SmartHome import process_smart_home_command, SMART_HOME_ACTIONS
from Tasks.Websites import open_website, COMMAND_URLS

# ======================[ Loading model and Creating Global Variables ]=================== #


print("Loading model...")
config = XttsConfig()
config.load_json("Voices\\Noelle\\config.json")
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir="Voices\\Noelle", use_deepspeed=False)
model.cuda()

print("Computing speaker latents...")
gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=["Voices\\Noelle\\NoelleVocals.wav"])

# TTS and speech recognition setup
recognizer = sr.Recognizer()
pygame.mixer.init()


# Flags and logs initialization
is_assistant_speaking = False
assistant_message_log = []

# Preparing initial system message for assistant log
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
openai.api_key = OpenAIKey

def ProcessResponse(text):
    global is_assistant_speaking
    # Append user message to the assistant's log
    assistant_message_log.append({"role": "user", "content": text})
    
    # Check if there's enough messages for a proper conversation
    if len(assistant_message_log) >= 2:
        
        # Make an OpenAI API call
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=assistant_message_log,
            max_tokens=50,
            temperature=0.7
        )
        
        # Get the text response from the API call
        response_text = completion.choices[0].message['content']
        
        # Save the response to a text file
        with open("Responses.txt", "a") as file:
            file.write(response_text + "\n")

        # Add the response to the log
        assistant_message_log.append({"role": "assistant", "content": response_text})

        # Set the flag to True to indicate the assistant is speaking
        is_assistant_speaking = True

        # Speak the response
        print("Inference...")
        out = model.inference(
            response_text,
            "en",
            gpt_cond_latent,
            speaker_embedding,
            temperature=0.7,
        )
        torchaudio.save("Response.wav", torch.tensor(out["wav"]).unsqueeze(0), 24000)
        Response = pygame.mixer.Sound('Response.wav')
        Response.play()

        # Wait for the TTS response to finish playing
        while pygame.mixer.get_busy():
            pass

        # Set the flag to False as the assistant has finished speaking
        is_assistant_speaking = False


# ======================[ COMMAND PROCESSING ]============================== #

# Command processing and speech recognition as ProcessCommands
async def ProcessCommands():
    global is_assistant_speaking

    commands_buffer = []  # To store accumulated commands while 'ctrl' is held down
    print("I'm here! What can I do for you?")
    with sr.Microphone() as source:
        while True:  # Keep the program running
            if keyboard.is_pressed('ctrl'):

                while True:  # Continuously listen until 'ctrl' is released
                    if not keyboard.is_pressed('ctrl'):  # Check if 'ctrl' is released
                        break  # Exit the loop if 'ctrl' is released

                    if is_assistant_speaking:
                        continue  # Skip if the assistant is currently speaking
                    audio = recognizer.listen(source)
                    
                    try:
                        command = recognizer.recognize_google(audio).lower()
                        commands_buffer.append(command)  # Store commands in the buffer
                    except sr.UnknownValueError:
                        print("Sorry, I didn't catch that.")
                    except sr.RequestError as e:
                        print(f"Could not request results; {e}")

                    await asyncio.sleep(0.1)  # Adjust sleep duration if needed

                # 'ctrl' key released, process accumulated commands
                if commands_buffer:
                    for command in commands_buffer:
                        if any(keyword in command for keyword in COMMAND_URLS):
                            await open_website(command)
                        elif any(phrase in command for phrase in SMART_HOME_ACTIONS):
                            await process_smart_home_command(command)
                        else:
                            ProcessResponse(command)
                    commands_buffer = []
                    print("Command Processed")

# Main entry point
if __name__ == "__main__":
    asyncio.run(ProcessCommands())



