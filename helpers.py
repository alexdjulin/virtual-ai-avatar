from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
import csv
import os
import numpy as np
import soundfile as sf
import sounddevice as sd
from elevenlabs import set_api_key, generate, save, Voice, VoiceSettings
import speech_recognition as sr

import dotenv
dotenv.load_dotenv()
set_api_key(os.getenv('ELEVENLABS_API_KEY', ''))

EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"


def get_openai_client():
    '''
    Create client instance
    '''
    return OpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))


def ask_chat_gpt(messages: str, model: str = GPT_MODEL) -> tuple:
    '''
    Create client instance and return chat response
    '''

    client = get_openai_client()
    completion = client.chat.completions.create(model=model, messages=messages)

    answer = completion.choices[0].message.content
    tokens = completion.usage.prompt_tokens, completion.usage.completion_tokens

    return answer, tokens


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_embeddings(answer: str, model: str = EMBEDDING_MODEL) -> None:
    '''Generate embeddings for an input string'''

    client = get_openai_client()
    answer = answer.replace("\n", " ")  # replace newlines
    return client.Embedding.create(input=answer, model=model)["data"][0]["embedding"]


def load_from_csv(csvfile: str) -> dict:
    '''
    Loads contents from csv file into a qna dict
    '''

    qna_dict = {}

    try:
        with open(csvfile, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader, None)  # skip header
            for row in reader:
                question, answer = row
                qna_dict[question] = answer
            print(f"Answers have been read from {csvfile}.")

    except Exception as e:
        print(f"Error reading from CSV file: {e}")

    return qna_dict


def write_to_csv(csvfile: str, qna_dict: dict) -> None:
    '''
    Write contents of a qna dict to a csv file
    '''

    try:
        with open(csvfile, 'a', newline='') as csvfile:
            fieldnames = ['Question', 'Answer']
            writer = csv.DictWriter(csvfile, quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
            for question, answer in qna_dict.items():
                writer.writerow({'Question': question, 'Answer': answer})

    except Exception as e:
        print(f"Error writing to CSV file: {e}")


def generate_tts(text: str, play: bool = False) -> np.ndarray:
    '''
    Generate audio from text using elevenlabs and return as numpy array
    '''

    audio = 'audio.wav'
    model = "eleven_multilingual_v2"
    voice = Voice(
        voice_id='AYOhfsTRHxv5o93aSW3L',  # Alex_v02_fr
        settings=VoiceSettings(stability=0.75, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
    )
    generation = generate(text=text, voice=voice, model=model)
    save(generation, audio)

    # Load the WAV file into a numpy array
    data, sample_rate = sf.read(audio)
    wavarr = np.array(data, dtype=np.float32)

    # Play the audio using sounddevice
    if play:
        sd.play(data, sample_rate)
        sd.wait()

    # Delete the audio file and return numpy array
    os.remove(audio)
    return wavarr


def record_voice() -> str:
    '''
    Record voice and return text transcription
    '''

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Recording...")
        audio = recognizer.listen(source)

    try:
        print("Transcribing...")
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"Transcription: {text}")
    except sr.UnknownValueError:
        print("Could not understand the audio.")
    except sr.RequestError:
        print("Error connecting to Google API.")

    return text