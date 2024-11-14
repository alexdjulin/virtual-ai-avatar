# Virtual AI Avatar
A realistic AI-driven clone of myself, using my face and voice, to chat and interact with.

## Use-Case Example

<a href="https://youtu.be/WZQRwoXRtgA" target="_blank"><img width="525" alt="Screenshot 2024-11-14 103109" src="https://github.com/user-attachments/assets/5c43554c-f05e-4c31-9904-676989eb2272">


## Description
This is the output of my AI avatar chat project, using Google speech recognition, OpenAI chat completion and Elevenlabs voice cloning.

The code repo is covering the AI-chat interface only (yellow blocks), not the lipsync generation (in green) or the avatar creation and rendering (in red), which are done in 3rd-party software.

![ai_avatar_flowchart](https://github.com/user-attachments/assets/b4e4dd03-4fb3-4521-bbcb-de2e6d2e98e4)

## Installation
Clone the project, create a virtual environment, activate it and install all the modules listed in the requirements file.

This project is using Python 3.12.1 but should work on earlier python3 versions too.

```shell
git clone https://github.com/alexdjulin/virtual-ai-avatar.git
cd virtual-ai-avatar
python -m venv .venv
.venv/Scripts/activate.bat
pip install -r requirements.txt
```

Rename ```config_template.yaml``` in ```config.yaml``` and edit or complete the values inside, like your API keys, AI models and settings, avatar info, paths, etc.

## Usage
Call main.py to start the tool and chose between the __Create Avatar Story__ and the __Chat With Avatar__ modes.

Alternatively you can pass arguments to start in Chat mode directly and specify input and output methods (text/voice and language) if you know the corresponding choice.

```python
# chose mode
python main.py

# input voice de_DE, output voice
python main.py -i 3 -o 2
```
