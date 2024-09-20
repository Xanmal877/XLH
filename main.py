# Built-in Imports
import logging
import threading
import time
import queue

# Third-party Imports
import numpy as np
import speech_recognition as sr
import pystray
from PIL import Image
import tkinter as tk
from tkinter import scrolledtext
import webrtcvad
import ollama

logging.basicConfig(level=logging.INFO)

name = "Xanmal"
aiName = "llama2-uncensored"

class TrayIconHandler:
    def __init__(self, command_handler):
        self.command_handler = command_handler
        self.create_tray_icon()

    def create_tray_icon(self):
        try:
            icon_image = Image.open("icon.png").convert("RGBA")
            self.tray_icon = pystray.Icon("AI Assistant", icon_image, menu=self.create_menu())
        except Exception as e:
            print(f"Error loading image: {e}")

    def create_menu(self):
        return pystray.Menu(
            pystray.MenuItem('Show Chat', self.show_chat_popup),
            pystray.MenuItem('Exit', self.exit_action)
        )

    def show_chat_popup(self, icon=None, item=None):
        self.command_handler.open_chat_window()

    def exit_action(self, icon, item):
        self.command_handler.should_exit.set()
        icon.stop()

    def run(self):
        self.tray_icon.run()

class AudioHandler:
    def __init__(self, chatInterface):
        self.recognizer = sr.Recognizer()
        self.audioQueue = queue.Queue()
        self.shouldExit = threading.Event()
        self.vad = webrtcvad.Vad(1)
        self.sampleRate = 16000
        self.frameDuration = 30
        self.frameSize = int(self.sampleRate * self.frameDuration / 1000)
        self.chatInterface = chatInterface

        # Start listening and processing threads
        threading.Thread(target=self.ListenContinuously, daemon=True).start()
        threading.Thread(target=self.ProcessAudioQueue, daemon=True).start()

    def ListenContinuously(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Listening...")
            while not self.shouldExit.is_set():
                try:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    self.CheckForSpeechChunks(audio)
                    time.sleep(0.05)
                except sr.WaitTimeoutError:
                    logging.debug("Listen timeout, continuing...")
                except Exception as e:
                    logging.error(f"Error during listening: {e}")

    def CheckForSpeechChunks(self, audio):
        audioData = np.frombuffer(audio.frame_data, dtype=np.int16)
        for start in range(0, len(audioData), self.frameSize):
            end = min(start + self.frameSize, len(audioData))
            frame = audioData[start:end]
            if self.vad.is_speech(frame.tobytes(), self.sampleRate):
                self.audioQueue.put(audio)
                break

    def ProcessAudioQueue(self):
        while not self.shouldExit.is_set():
            try:
                audio = self.audioQueue.get(timeout=1)  # Non-blocking with timeout
                self.ProcessAudio(audio)
            except queue.Empty:
                continue

    def ProcessAudio(self, audio):
        try:
            transcribedText = self.recognizer.recognize_google(audio)
            logging.info("{name} said: {transcribedText}")
            self.chatInterface.DisplayMessage(name + ":", transcribedText)
            self.chatInterface.DisplayMessage(aiName + ":", LLMResponse(transcribedText))
            return transcribedText
        except sr.UnknownValueError:
            logging.info("Could not understand audio")
        except sr.RequestError:
            logging.error("Speech recognition service unavailable")

class ChatInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("{aiName} Chatbot")
        self.root.geometry("500x600")
        self.root.configure(bg="#343541")

        # Conversation display area
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled', bg="#343541", fg="#eaeaea", font=("Helvetica", 12))
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Input field for typing messages
        self.entry_frame = tk.Frame(self.root, bg="#40414f")
        self.entry_frame.pack(fill=tk.X, padx=10, pady=10)

        self.message_entry = tk.Entry(self.entry_frame, bg="#40414f", fg="#eaeaea", font=("Helvetica", 16), bd=0, insertbackground="#eaeaea")
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        self.message_entry.bind("<Return>", self.SendMessage)

        # Send button (optional)
        self.send_button = tk.Button(self.entry_frame, text="Send", bg="#10a37f", fg="#eaeaea", command=self.SendMessage)
        self.send_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def SendMessage(self, event=None):
        transcribedText = self.message_entry.get()
        if transcribedText.strip():
            self.DisplayMessage(name + ":", transcribedText)  # Display user's message

            # Call LLMResponse to get AI's response
            aiResponse = LLMResponse(transcribedText)  # Assuming LLMResponse is defined elsewhere
            self.DisplayMessage(aiName + ":", aiResponse)  # Display AI's response
            self.message_entry.delete(0, tk.END)  # Clear the input field

    def DisplayMessage(self, sender, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {message}\n", "tag-right" if sender == name else "tag-left")
        self.chat_display.yview(tk.END)  # Auto-scroll to the bottom
        self.chat_display.config(state='disabled')

def LLMResponse(transcribedText):
    response = ollama.chat(
        model=aiName,
        messages=[{'role': 'user', 'content': transcribedText}], stream=False,)
    llmResponse = response['message']['content']
    logging.info(f"{aiName}: {llmResponse}")
    return llmResponse


if __name__ == "__main__":
    chatInterface = ChatInterface()
    audioHandler = AudioHandler(chatInterface)
    chatInterface.root.mainloop()

    while not audioHandler.shouldExit.is_set():
        try:
            audio = audioHandler.audioQueue.get(timeout=1)
            transcribedText = audioHandler.ProcessAudio(audio)
            if transcribedText:
                # Get the AI response
                aiResponse = LLMResponse(transcribedText)
                # Display the AI response in the chat interface
                chatInterface.DisplayMessage(aiName + ":", aiResponse)
        except queue.Empty:
            continue

    audioHandler.shouldExit.set()





