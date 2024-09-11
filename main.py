import torch
from TTS.api import TTS
from pydub import AudioSegment
from pydub.playback import play
import os
import speech_recognition as sr
import warnings
from queue import Queue
import logging
import threading
import time
import keyboard
import ollama


# Suppress specific warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module='pydub')
warnings.filterwarnings("ignore", category=FutureWarning, module='TTS')

# Set up logging
logging.basicConfig(level=logging.INFO)

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
ollama.pull('llama3.1')


class AIConversation:
    def __init__(self):
        self.message_queue = Queue()  # Queue for TTS messages
        self.audio_files = Queue()  # Queue for preloaded audio files
        self.audio_dir = "WavFiles/Output"
        self.next_file_number = 1
        self.recording = False
        self.toggle_pressed = False
        self.recognizer = sr.Recognizer()  # Define recognizer as an instance variable

        # Ensure the directory exists
        os.makedirs(self.audio_dir, exist_ok=True)

        self.audio_thread = threading.Thread(target=self.AudioPlaybackSetup)
        self.audio_thread.daemon = True  # Ensure the thread exits when the main program does
        self.audio_thread.start()

        self.listen_thread = threading.Thread(target=self.push_to_talk)
        self.listen_thread.daemon = True  # Ensure the thread exits when the main program does
        self.listen_thread.start()


    def push_to_talk(self):
        with sr.Microphone() as source:
            while True:
                if keyboard.is_pressed('space'):
                    if not self.recording:
                        print("Recording started.")
                        self.recording = True
                    # Listen and process audio only while space bar is pressed
                    audio = self.recognizer.listen(source, timeout=5)  # Adjust timeout as needed
                    if audio:
                        print("Processing...")
                        self.process_audio(audio)
                else:
                    if self.recording:
                        print("Recording stopped.")
                        self.recording = False
                time.sleep(0.1)  # Prevent busy-waiting


    def process_audio(self, audio):
        try:
            command = self.recognizer.recognize_google(audio)
            print(f"User: {command}")
            self.MessageAI(command)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError:
            print("Request error")


    def MessageAI(self, text):
        response = ollama.chat(
            model='Tamaneko',
            messages=[{'role': 'user', 'content': text}],
            stream=False,
        )

        AIResponse = response['message']['content']
        print(f"AI Response: {AIResponse}")

        segments = AIResponse.split('.')
        for segment in segments:
            trimmed_segment = segment.strip()
            if trimmed_segment:
                self.preload_audio(trimmed_segment + '.')

        return AIResponse



    def preload_audio(self, text):
        try:
            # Generate and save the audio file
            file_path = os.path.join(self.audio_dir, f"Output{self.next_file_number}.wav")
            tts.tts_to_file(text=text, speaker_wav="WavFiles/Training.wav", language="en", file_path=file_path)
            logging.info(f"Preloaded audio file saved as '{file_path}'")
            print(f"Preloaded audio file saved as '{file_path}'")

            # Increment the file number for the next file
            self.next_file_number += 1

            # Add the preloaded file to the queue
            self.audio_files.put(file_path)
        except Exception as e:
            logging.error(f"An error occurred during TTS setup: {e}")

    def AudioPlaybackSetup(self):
        while True:
            if not self.audio_files.empty():
                file_path = self.audio_files.get()
                print(f"Playing audio file '{file_path}'")
                try:
                    # Play the audio file
                    self.play_audio(file_path)
                except Exception as e:
                    logging.error(f"An error occurred during audio playback: {e}")
            else:
                # Sleep briefly to prevent busy-waiting
                time.sleep(0.1)

    def play_audio(self, file_path):
        try:
            # Play the audio file
            audio = AudioSegment.from_wav(file_path)
            play(audio)
            logging.info(f"Playing audio file '{file_path}'")
        except Exception as e:
            logging.error(f"An error occurred during audio playback: {e}")
        finally:
            # Delete the audio file after playing
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Audio file '{file_path}' deleted.")
                print(f"Audio file '{file_path}' deleted.")


if __name__ == "__main__":
    Talk = AIConversation()

    while True:
        time.sleep(1)
