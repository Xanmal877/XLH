# AI Conversation Application

## Overview

This application integrates speech recognition and AI response generation for interactive conversations. It listens to audio commands through the microphone, processes these commands with an AI model, and provides responses. The application also includes a system tray icon for managing conversation history and interaction with the application.

## Features

- **Speech Recognition**: Converts spoken commands into text.
- **AI Response Generation**: Uses an AI model to generate responses based on the recognized text.
- **Conversation History**: Stores and displays a history of interactions.
- **System Tray Icon**: Provides quick access to conversation history and application exit options.

## Requirements

- **Python**: 3.10.6 or later
- **CUDA**: 11.3 or later
- **cuDNN**: 9.0 or later
- **FFmpeg**: Required for audio processing
- **Ollama**: For AI response generation

## Installation

1. Run `installs.py` to install necessary packages.
2. Run `update.bat` to perform additional setup tasks.
3. Place an icon image named `icon.png` in the project directory.
4. Run `run.bat` to start the application.

## Usage

- **Always Listening**: The application continuously listens for audio commands, processes them, and generates responses.
- **Conversation History**: Access and review past interactions by clicking the system tray icon and selecting "Show Conversation."
- **Exit Application**: Click the system tray icon and select "Exit" to close the application.
