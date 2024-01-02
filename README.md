# AI Conversation Application

## Overview

This AI-powered application integrates text-to-speech (TTS) and speech recognition to facilitate interactive conversations. It listens for audio commands, processes them with an AI model, and responds using synthesized speech. The application includes features for playing and managing pre-recorded audio files.

## Features

- **Speech Recognition**: Converts speech to text using the microphone.
- **AI Response Generation**: Retrieves and processes AI model responses.
- **Text-to-Speech (TTS)**: Synthesizes spoken responses from AI text outputs.
- **Audio Playback**: Manages and plays pre-recorded audio files.
- **Push-to-Talk**: Records audio only while the space bar is pressed.

## Requirements

- **Python**: 3.10.6 or later
- **PyTorch**: 1.12.1 with CUDA support
- **CUDA**: 11.3 or later
- **cuDNN**: 9.0 or later
- **FFmpeg**
- **Ollama**

## Installation

- Run Update.bat
- Grab wav file 10-20 seconds long of a Voice
- name the wav file "Training.wav"
- put the "Training.wav" file in WavFiles
- Run Run.bat


## Usage

- Push-to-Talk: Press and hold the space bar to start recording. The application will process the audio, generate a response, and play it back.
- Processing Audio: The recorded audio is converted to text, processed by the AI model, and then synthesized into speech for playback.
- Audio Playback: Pre-recorded responses are played back and deleted after use.
