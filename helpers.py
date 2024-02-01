from logger import get_logger
from datetime import datetime
from time import sleep
from openai import OpenAI
import csv
import os
from elevenlabs import Voice, VoiceSettings, generate, play
import speech_recognition as sr
from textwrap import dedent
from terminal import GREY, RESET, CLEAR

from config_loader import config
LOG = get_logger(os.path.splitext(os.path.basename(__file__))[0])


def format_string(prompt: str) -> str:
    '''
    Removes tabs, line breaks and extra spaces from strings. This is useful
    when formatting prompts to send to chatGPT or to save to a csv file

    Args:
        prompt (str): prompt to format

    Return:
        (str): formatted prompt
    '''

    # remove tabs and line breaks
    prompt = dedent(prompt).replace('\n', ' ').replace('\t', ' ')

    # remove extra spaces
    while '  ' in prompt:
        prompt = prompt.replace('  ', ' ')

    return prompt.strip()


def ask_chat_gpt(messages: str, model: str = config['openai_model']) -> tuple:
    '''
    Return chat completion answer + token counts

    Args:
        messages (str): prompt to send to chatGPT
        model (str, optional): model to use.

    Return:
        (tuple): answer (str), tokens (int, int)
    '''

    # create client instance
    client = OpenAI(api_key=config['openai_api_key'])

    # send message to chatGPT
    completion = client.chat.completions.create(model=model, messages=messages)

    # extract and return answer and tokens count
    answer = completion.choices[0].message.content
    tokens = completion.usage.prompt_tokens, completion.usage.completion_tokens

    return answer, tokens


def load_from_csv(csvfile: str) -> dict:
    '''
    Loads question and answers from csv file into a dict

    Args:
        csvfile (str): path to csv file

    Return:
        (dict): dict with question and answers

    Raises:
        Exception: if error reading csv file
    '''

    qna_dict = {}

    try:
        with open(csvfile, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # store avatar name
            qna_dict["What's your name?"] = f"My name is {config['avatar_name']}."
            for row in reader:
                question, answer = row
                qna_dict[question] = answer
            LOG.debug(f"Answers have been read from {csvfile}.")

    except Exception as e:
        LOG.error(f"Error reading from CSV file: {e}")
        print(f'{GREY}Failed to load avatar story (see log).{RESET}')

    return qna_dict


def write_to_csv(csvfile: str, *strings: list, timestamp: bool = False) -> bool:
    '''
    Adds strings to a csv file on a new row

    Args:
        csvfile (str): path to csv file
        *strings (list): strings to add as columns to csv file
        timestamp (bool): first column should be a timestamp

    Return:
        (bool): True if successful, False otherwise

    Raises:
        Exception: if error writing to csv file
    '''

    try:
        with open(csvfile, mode='a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, doublequote=True)
            # remove tabs, line breaks and extra spaces
            safe_strings = [format_string(s) for s in strings]
            if timestamp:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                safe_strings = [timestamp] + safe_strings
            csv_writer.writerow(safe_strings)

    except Exception as e:
        LOG.error(f"Error writing to CSV file: {e}")
        return False

    return True


def generate_tts(text: str) -> None:
    '''
    Generates audio from text using elevenlabs and plays it

    Args:
        text (str): text to generate audio from
    '''

    # get api-key and model from settings
    api_key = config['elabs_api_key']
    model = config['elabs_model']

    # set-up elevenlabs voice settings
    voice = Voice(
        voice_id=config['elabs_voice_id'],
        settings=VoiceSettings(
            stability=config['elabs_stability'],
            similarity_boost=config['elabs_similarity_boost'],
            style=config['elabs_style'],
            use_speaker_boost=config['elabs_use_speaker_boost']
            )
    )

    # generate audio data
    try:
        generation = generate(text=text, api_key=api_key, voice=voice, model=model)

    except Exception as e:
        LOG.error(f"Error generating and playing audio: {e}. Voice deactivated.")
        # print answer and exit
        print(f'{CLEAR}{text}')
        return

    # print answer once generated
    print(f'{CLEAR}{text}')

    # play audio file
    play(generation)


def record_voice(language, exit_chat) -> str or None:
    '''
    Record voice and return text transcription.
    Args are passed by reference as mutable dicts so they can be modified on keypress and updated here.

    Args:
        language (dict): language to use {'value': str}
        exit_chat (dict): chat exit flag {'value': bool}

    Return:
        (str | None): text transcription

    Raises:
        UnknownValueError: if audio could not be transcribed
        RequestError: if error connecting to Google API
    '''

    text = ''
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    try:

        with microphone as source:

            print(f"{CLEAR}{GREY}(listen {language['value']}){RESET}", end=' ', flush=True)
            timeout = config['speech_timeout']
            audio = recognizer.listen(source, timeout=timeout)

            print(f"{CLEAR}{GREY}(transcribe {language['value']}){RESET}", end=' ', flush=True)
            text = recognizer.recognize_google(audio, language=language['value'])

            if not text:
                raise sr.UnknownValueError

            return text.capitalize()

    except sr.WaitTimeoutError:
        if config['use_keyboard']:
            print(f"{CLEAR}{GREY}Can't hear you. Please try again.{RESET}", end=' ', flush=True)
        else:
            if not exit_chat['value']:
                # start listening again
                record_voice(language, exit_chat)

    except sr.UnknownValueError:
        print(f"{CLEAR}{GREY}Can't understand audio. Please try again.{RESET}", end=' ', flush=True)
        sleep(2)

    except sr.RequestError:
        print(f"{CLEAR}{GREY}Error connecting to Google API. Please try again.{RESET}", end=' ', flush=True)
        sleep(2)

    return None
