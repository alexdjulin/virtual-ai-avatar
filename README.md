# Virtual AI Avatar
A realistic AI-driven clone of myself, using my face and voice, to chat and interact with.

## Use-Case Example

https://github.com/alexdjulin/virtual-ai-avatar/assets/53292656/147f2466-f327-4ad0-8a0d-691da8f03389

_Here is a short extract, contact me for the full demo video._

## Description
This is the output of my AI avatar chat project, using Google speech recognition, OpenAI chat completion and Elevenlabs voice cloning.

The code repo is covering the AI-chat interface only (yellow blocks), not the lipsync generation (in green) or the avatar creation and rendering (in red), which are done in 3rd-party software.

![code_structure_diagram](https://github.com/alexdjulin/virtual-ai-avatar/assets/53292656/f0951fe9-be56-4551-ada4-06ef4d8e9a43)

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
