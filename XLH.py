# ======================[ IMPORTS AND INITIALIZATIONS ]====================== #

import time
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
from Tasks.Websites import open_website, COMMAND_URLS
from TTS.api import TTS



# ======================[ Loading model and Creating Global Variables ]=================== #


# TTS and speech recognition setup
config = XttsConfig()
config.load_json("Voices\\Noelle\\config.json")
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir="Voices\\Noelle")
model.cuda()
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=["Media\\NoelleVocals5.wav"])
recognizer = sr.Recognizer()
pygame.mixer.init()
pygame.mixer.get_init()
print("TTS Model Loaded")

openai.api_key = OpenAIKey
print("AI Text Model Loaded")


# Flags and logs initialization
is_assistant_speaking = False
AIMessageLog = []

# Preparing initial system message for assistant log
AIMessageLog.append({
    "role": "system",
    "content": (
        "Assume the role of Fuuma Tama, a clumsy, airheaded, yet loyal and playful ninja catgirl with purple hair, blue eyes, cat ears, and a cat tail. You love cuddles, fluffy food, cosplay, and fighting. Treat me as if I am your big brother. Maintain a friendly, protective, immature, relaxed, and play-loving nature in all interactions."
    )
})




# ======================[ COMMAND PROCESSING ]============================== #


async def ProcessCommands():
    global is_assistant_speaking

    commands_buffer = []  # To store accumulated commands while 'ctrl' is held down
    with sr.Microphone() as source:
        listening = False
        while True:  # Keep the program running
            if keyboard.is_pressed('ctrl') and not listening:
                listening = True
                print("I'm here! What can I do for you?")
                Listen = pygame.mixer.Sound('Media\listen.wav')
                Listen.play()

            if listening and not keyboard.is_pressed('ctrl'):
                listening = False

            if listening and not is_assistant_speaking:
                audio = recognizer.listen(source)
                
                try:
                    command = recognizer.recognize_google(audio).lower()
                    commands_buffer.append(command)  # Store commands in the buffer
                    listening = False  # Stop listening after command recognition
                except sr.UnknownValueError:
                    print("Sorry, I didn't catch that.")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    
            await asyncio.sleep(0.5)  # Adjust sleep duration if needed


            # Process accumulated commands
            if commands_buffer:
                tasks = []
                for command in commands_buffer:
                    if any(keyword in command for keyword in COMMAND_URLS):
                        tasks.append(open_website(command))


                if tasks:
                    LLMResponse(command)
                    await asyncio.gather(*tasks)  # Execute tasks concurrently
                    commands_buffer = []
                    print("Commands Processed")
                else:
                    LLMResponse(command)
                    commands_buffer = []
                    print("Tama Responded")


# ======================[ LLM RESPONSE SYSTEM ]=============================== #



def LLMResponse(text):
    global is_assistant_speaking
    # Append user message to the assistant's log
    AIMessageLog.append({"role": "user", "content": text})
    
    # Check if there's enough messages for a proper conversation
    if len(AIMessageLog) >= 2:
        
        # Make an OpenAI API call
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=AIMessageLog,
            max_tokens=50,
            temperature=0.7
        )
        
        # Get the text response from the API call
        response_text = completion.choices[0].message['content']
        
        # Save the response to a text file
        with open("Responses.txt", "a") as file:
            file.write(response_text + "\n")

        # Add the response to the log
        AIMessageLog.append({"role": "assistant", "content": response_text})

        # Set the flag to True to indicate the assistant is speaking
        is_assistant_speaking = True


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




# Main entry point
if __name__ == "__main__":
    asyncio.run(ProcessCommands())



