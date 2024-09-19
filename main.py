# Built-in Imports
import logging
import threading
import time
import queue
import subprocess

# Third-party Imports
import numpy as np
import speech_recognition as sr
import pystray
from PIL import Image
import tkinter as tk
from tkinter import scrolledtext
import webrtcvad
import ollama


class AudioHandler:
    def __init__(self, command_handler):
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()
        self.should_exit = threading.Event()
        self.vad = webrtcvad.Vad(1)  # Set mode to 1 (less aggressive)
        self.sample_rate = 16000
        self.frame_duration = 30
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        self.command_handler = command_handler

        threading.Thread(target=self.listen_continuously, daemon=True).start()
        threading.Thread(target=self.process_audio_queue, daemon=True).start()

    def process_audio_chunks(self, audio):
        audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)
        for start in range(0, len(audio_data), self.frame_size):
            end = min(start + self.frame_size, len(audio_data))
            frame = audio_data[start:end]
            if self.vad.is_speech(frame.tobytes(), self.sample_rate):
                self.audio_queue.put(audio)
                break

    def listen_continuously(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Listening...")
            while not self.should_exit.is_set():
                try:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    self.process_audio_chunks(audio)
                    time.sleep(0.05)
                except sr.WaitTimeoutError:
                    logging.debug("Listen timeout, continuing...")
                except Exception as e:
                    logging.error(f"Error during listening: {e}")

    def process_audio_queue(self):
        while not self.should_exit.is_set():
            try:
                audio = self.audio_queue.get(timeout=1)
                self.command_handler.process_audio(audio)
            except queue.Empty:
                continue


class CommandHandler:
    def __init__(self, tray_icon_handler):
        self.conversation_history = []
        self.tray_icon_handler = tray_icon_handler
        self.should_exit = threading.Event()

    def process_audio(self, audio):
        recognizer = sr.Recognizer()
        try:
            command = recognizer.recognize_google(audio)
            logging.info(f"You said: {command}")
            self.handle_command(command)
        except sr.UnknownValueError:
            logging.info("Could not understand audio")
        except sr.RequestError:
            logging.error("Speech recognition service unavailable")

    def handle_command(self, command):
        response = ollama.chat(
            model='Tamaneko',
            messages=[{'role': 'user', 'content': command}],
            stream=False,
        )
        ai_response = response['message']['content']
        logging.info(f"AI: {ai_response}")

        self.conversation_history.append(f"You said: {command}")
        self.conversation_history.append(f"AI: {ai_response}")

        self.tray_icon_handler.show_chat_bubble("AI Response", ai_response)

        if "EXECUTE:" in ai_response:
            command_to_execute = ai_response.split("EXECUTE:")[1].strip()
            self.execute_command(command_to_execute)

    def execute_command(self, command):
        try:
            result = subprocess.run(command, shell=True, text=True, capture_output=True, timeout=30)
            if result.returncode == 0:
                logging.info(f"Command executed successfully: {result.stdout}")
            else:
                logging.error(f"Command failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            logging.error("Command execution timed out")
        except Exception as e:
            logging.error(f"Error executing command: {e}")


class TrayIconHandler:
    def __init__(self, command_handler):
        self.command_handler = command_handler
        self.create_tray_icon()

    def create_tray_icon(self):
        icon_image = Image.open("icon.png")  # Ensure this file exists
        self.tray_icon = pystray.Icon("AI Assistant", icon_image, menu=self.create_menu())
        self.tray_icon.on_click = self.on_tray_icon_click
        threading.Thread(target=self.tray_icon.run).start()

    def create_menu(self):
        return pystray.Menu(
            pystray.MenuItem('Show Conversation', self.show_conversation_popup),
            pystray.MenuItem('Exit', self.exit_action)
        )

    def on_tray_icon_click(self, icon, item):
        if item.text == 'Show Conversation':
            self.show_conversation_popup(icon, item)
        elif item.text == 'Exit':
            self.exit_action(icon, item)

    def show_conversation_popup(self, icon, item):
        def show_window():
            root = tk.Tk()
            root.title("Conversation History")
            root.geometry("400x800")

            # Set window to stay on top
            root.attributes('-topmost', True)

            text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
            text_area.insert(tk.END, "\n".join(self.command_handler.conversation_history))
            text_area.configure(state='disabled')
            text_area.pack(expand=True, fill='both')

            root.mainloop()

        threading.Thread(target=show_window).start()

    def show_chat_bubble(self, title, message):
        def display_bubble():
            root = tk.Tk()
            root.title(title)
            root.geometry("300x300")

            # Set window to stay on top
            root.attributes('-topmost', True)

            # Create a label for the message
            label = tk.Label(root, text=message, bg="#f0f0f0", fg="#000000", padx=10, pady=10, wraplength=280)
            label.pack(expand=True)

            # Set a timer to close the window after 20 seconds
            root.after(5000, root.destroy)

            root.mainloop()

        threading.Thread(target=display_bubble).start()

    def exit_action(self, icon):
        self.command_handler.should_exit.set()
        icon.stop()


if __name__ == "__main__":
    command_handler = CommandHandler(tray_icon_handler=None)
    tray_icon_handler = TrayIconHandler(command_handler)
    command_handler.tray_icon_handler = tray_icon_handler

    audio_handler = AudioHandler(command_handler)

    try:
        logging.info("AI Assistant started. Press Ctrl+C to exit.")
        while not command_handler.should_exit.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Exiting...")
    finally:
        command_handler.should_exit.set()
        logging.info("AI Assistant stopped.")
