import os
from time import sleep
import helpers
import keyboard
import threading
import re
from terminal import CYAN, RED, GREEN, GREY, RESET, CLEAR

# import config and create logger
from config_loader import config
from logger import get_logger
LOG = get_logger(os.path.splitext(os.path.basename(__file__))[0])

# create variables for most used settings
AVATAR_NAME = config['avatar_name']
AVATAR_DESCRIPTION = config['avatar_description']
USER_NAME = config['user_name']
AVATAR_STORY_CSV = config['avatar_story'].replace('<avatar_name>', AVATAR_NAME.lower())
CHAT_HISTORY_CSV = config['chat_history'].replace('<avatar_name>', AVATAR_NAME.lower())
LOG_FILE = config['log_file'].replace('<avatar_name>', AVATAR_NAME.lower())

# create required folders if needed
os.makedirs(os.path.dirname(AVATAR_STORY_CSV), exist_ok=True)
os.makedirs(os.path.dirname(CHAT_HISTORY_CSV), exist_ok=True)


class AiAvatar:
    '''
    This class defines an AI avatar and methods to interact with it
    '''

    def __init__(self) -> None:
        '''
        Create class instance
        '''

        # create and load avatar story
        self.story_dict = helpers.load_from_csv(AVATAR_STORY_CSV)

        # input / output methods
        self.input = None
        self.output = None
        self.language = {'value': None}  # use a dict to pass language by reference to helpers

        # flags
        self.recording = False
        self.exit_chat = {'value': False}  # use a dict to pass flag by reference to helpers

        # token count for price estimation
        self.prompt_tokens = 0
        self.completion_tokens = 0

        # thread object to handle chat tasks
        self.chat_thread = None


    def __repr__(self) -> str:
        '''
        Returns all avatar information and story to print

        Return:
            str: avatar name, story and blacklisted questions

        '''

        result = f"{CYAN}# NAME #{RESET}\n{AVATAR_NAME}\n"

        # prints questions and answers
        if self.story_dict:
            result += f'\n{CYAN}# QUESTIONS / ANSWERS #{RESET}\n'
            id = 1
            for q, a in self.story_dict.items():
                result += f'{CYAN}{id}. {q}{RESET} {a}\n'
                id += 1

        return result


    def create_avatar_story(self, subject: str = 'any subject', questions: int = 5) -> None:
        '''
        Build your avatar backstory by answering questions from chatGPT about you/him/her
        Add skipped questions to blacklist and save answers to csv file

        Args:
            subject (str): subject of the questions
            questions (int): number of questions to ask

        Raises:
            Exception: if error generating question

        '''

        for _ in range(questions):

            # generate prompt including list of given answers
            messages = [
                {
                    'role': 'system',
                    'content': helpers.format_string(f"""
                        You are chatting with your interlocutor and you want to know everything about him.
                        - Limit your questions to the following subject: {subject}.
                        - Don't ask a question you already asked.
                        - Don't ask a question if the user doesn't want to answer it.
                        - Limit your answers to one single question.
                        """
                    )
                }
            ]

            # add already asked questions and answers from story
            for question, answer in self.story_dict.items():
                messages.append({"role": "assistant", "content": question})
                messages.append({"role": "user", "content": answer})

            # invite next question
            messages.append({"role": "user", "content": "What else do you want to know about me?"})

            try:
                question, tokens = helpers.ask_chat_gpt(messages=messages)
                self.prompt_tokens += tokens[0]
                self.completion_tokens += tokens[1]
                print(f"\n{GREEN}{AVATAR_NAME}:{RESET} {question}")
                answer = input(f'{RED}{USER_NAME}: {RESET}')

                if answer == '':
                    answer = "I don't want to answer that question."

                elif answer.lower() in {'quit', 'exit'}:
                    # exit program
                    break

                # add question/answer to csv
                self.story_dict[question] = answer
                helpers.write_to_csv(AVATAR_STORY_CSV, question, answer, timestamp=False)

            except Exception as error:
                LOG.error(f"Error generating question: {error}")

        print('Done asking questions')

    def chat_with_avatar(self, input_method: str = None, output_method: str = None) -> None:
        '''
        Starting point to chat with the avatar.

        Args:
            input_method (int): see available inputs in set_input_output_methods
            output_method (int): see available outputs in set_input_output_methods
        '''

        # define keyboard event to exit chat at any time
        keyboard.on_press_key("esc", self.on_esc_pressed)

        # set input and output methods (talk or text)
        self.set_input_output_methods(input_method, output_method)

        print(f'\n{GREY}Starting chat, please wait...{RESET}')

        # print, log and write new chat settings to csv file
        chat_settings = {
            'Input': self.input,
            'Output': self.output,
            'Language': self.language["value"],
            'Keyboard Mode': 'ON' if config['use_keyboard'] else 'OFF',
            'Language Hotkeys': 'ON' if config['language_hotkeys'] else 'OFF'
        }
        LOG.debug(f'Chat Started | {chat_settings}')
        helpers.write_to_csv(CHAT_HISTORY_CSV, 'NEW CHAT', ' | '.join([f'{k}: {v}' for k, v in chat_settings.items()]), timestamp=True)

        print(f'\n{CYAN}# CHAT START #{RESET}')
        print(' | '.join([f'{key}: {CYAN}{value}{RESET}' for key, value in chat_settings.items()]))

        # generate prompt
        self.messages = [
            {
                'role': 'system',
                'content': helpers.format_string(
                    f"""For the entire conversation follow these rules:
                    - Roleplay as {AVATAR_NAME}, {AVATAR_DESCRIPTION}.
                    - Never break character, do not reveal that you are an AI.
                    - Anways answer in the same language as the question.
                    - Keep your answers short, 1 or 2 sentences only.
                    - If you don't know an answer, invent one fitting your character.
                    """
                )
            }
        ]

        # add all question and answers from the avatar story to the chat prompt to give it context
        for question, answer in self.story_dict.items():
            self.messages.append({"role": "user", "content": question})
            self.messages.append({"role": "assistant", "content": answer})

        if self.exit_chat['value']:
            # exit program before starting chat if esc was pressed during setup
            exit()

        print(f'\n{RED}{USER_NAME}:{RESET}')

        # define the input method: text, direct chat or keyboard-activated chat
        if self.input == 'text':
            while not self.exit_chat['value']:
                # get user message
                new_message = input()
                if new_message.strip() == '':
                    # skip empty message or only spaces
                    continue
                if new_message in {'quit', 'exit'}:
                    # raise exit flag and exit loop on keywords
                    self.exit_chat['value'] = True
                    break
                # send message to chatGPT and get answer on separate thread
                self.chat_thread = threading.Thread(target=self.send_message_get_answer, args=[new_message])
                self.chat_thread.start()

        else:
            if config['language_hotkeys']:
                # define keyboard event to switch language at any time
                keyboard.on_press_key("2", self.on_2_pressed)
                keyboard.on_press_key("3", self.on_3_pressed)
                keyboard.on_press_key("4", self.on_4_pressed)
                keyboard.on_press_key("5", self.on_5_pressed)

            if config['use_keyboard']:
                # define keyboard event to trigger audio inpout
                keyboard.on_press_key("space", self.on_space_pressed)

                while not self.exit_chat['value']:
                    sleep(1)  # wait 1 second before checking again

            else:
                # use direct chat input
                while not self.exit_chat['value']:
                    if self.recording is False:
                        # start a new record thread
                        self.chat_thread = threading.Thread(target=self.record_message)
                        self.chat_thread.start()
                    sleep(1)  # wait 1 second before checking again

        # stop keyboard listener
        keyboard.unhook_all()

        # wait for chat thread to finish
        if self.chat_thread and self.chat_thread.is_alive():
            self.chat_thread.join()

        # print token count and cost estimation
        print(f'\n{CYAN}# CHAT END #{RESET}')
        self.print_token_count()

    def set_input_output_methods(self, input_method: str, output_method: str) -> None:
        '''
        Set input and output methods for chatting with the avatar
        INPUT can be text typing or voice recording (for voice, the language should be selected)
        OUTPUT can be a text print or voice transcription
        Input and output can use different methods
        '''

        # define input
        available_inputs = {'1': 'text', '2': 'en-EN', '3': 'de-DE', '4': 'fr-FR', '5': 'ro-RO'}

        if input_method not in available_inputs:
            # offer input choices
            print(f'\n{CYAN}# SELECT CHAT INPUT #{RESET}')
            print(f'{CYAN}1.{RESET} Voice OFF - Use {CYAN}text{RESET} input')
            print(f'{CYAN}2.{RESET} Voice ON  - I want to chat in {CYAN}English{RESET}')
            print(f'{CYAN}3.{RESET} Voice ON  - Ich möchte auf {CYAN}Deutsch{RESET} chatten')
            print(f'{CYAN}4.{RESET} Voice ON  - Je veux chatter en {CYAN}Français{RESET}')
            print(f'{CYAN}5.{RESET} Voice ON  - Vreau să vorbesc în limba {CYAN}română{RESET}')

            while not input_method in available_inputs:
                input_method = input('>> ')
                # exit program if esc was pressed
                if self.exit_chat['value']:
                    exit()

        # set input methode and language
        self.input = available_inputs[input_method]
        if self.input != 'text':
            self.language['value'] = self.input
            self.input = 'voice'

        # define output
        available_outputs = {'1': 'text', '2': 'talk'}

        if output_method not in available_outputs:
            # offer output choices
            print(f'\n{CYAN}# SELECT CHAT OUTPUT #{RESET}')
            print(f'{CYAN}1.{RESET} Voice OFF / Use {CYAN}text{RESET} output')
            print(f'{CYAN}2.{RESET} Voice ON / Avatar should {CYAN}talk{RESET}')

            while not output_method in available_outputs:
                output_method = input('>> ')
                # exit program if esc was pressed
                if self.exit_chat['value']:
                    exit()

        # set output method (language not needed for output)
        self.output = available_outputs[output_method]

    def on_space_pressed(self, e) -> None:
        ''' When space is pressed, start a thread to record your voice and send message to chatGPT '''
        if e.event_type == keyboard.KEY_DOWN and self.recording is False:
            self.chat_thread = threading.Thread(target=self.record_message)
            self.chat_thread.start()

    def on_esc_pressed(self, e) -> None:
        ''' When esc is pressed, raise exit_flag to terminate chat and any chat thread running '''
        if e.event_type == keyboard.KEY_DOWN and not self.exit_chat['value']:
            LOG.debug('Raising exit flag to terminate chat')
            self.exit_chat['value'] = True
            message = 'Ending chat, please wait...' if self.input == 'voice' else 'Ending chat, PRESS ENTER to close'
            print(f'{CLEAR}{GREY}{message}{RESET}', flush=True)

    def on_2_pressed(self, e) -> None:
        ''' When 2 is pressed, switch input language to English '''
        if e.event_type == keyboard.KEY_DOWN:
            LOG.debug('Switching input language to English')
            self.language['value'] = 'en-US'
            print(f"{CLEAR}{GREY}(language set to {self.language['value']}){RESET}", end=' ', flush=True)

    def on_3_pressed(self, e) -> None:
        ''' When 3 is pressed, switch input language to German '''
        if e.event_type == keyboard.KEY_DOWN:
            LOG.debug('Switching input language to German')
            self.language['value'] = 'de-DE'
            print(f"{CLEAR}{GREY}(language set to {self.language['value']}){RESET}", end=' ', flush=True)

    def on_4_pressed(self, e) -> None:
        ''' When 4 is pressed, switch input language to French '''
        if e.event_type == keyboard.KEY_DOWN:
            LOG.debug('Switching input language to French')
            self.language['value'] = 'fr-FR'
            print(f"{CLEAR}{GREY}(language set to {self.language['value']}){RESET}", end=' ', flush=True)

    def on_5_pressed(self, e) -> None:
        ''' When 5 is pressed, switch input language to Romanian '''
        if e.event_type == keyboard.KEY_DOWN:
            LOG.debug('Switching input language to Romanian')
            self.language['value'] = 'ro-RO'
            print(f"{CLEAR}{GREY}(language set to {self.language['value']}){RESET}", end=' ', flush=True)

    def record_message(self) -> None:
        '''
        Record voice and transcribe message

        Args:
            exit_chat (bool): chat exit flag
        '''

        self.recording = True
        new_message = None

        new_message = helpers.record_voice(self.language, self.exit_chat)

        # Process new message on success or ask user to try again if no message was recorded
        if new_message:
            self.send_message_get_answer(new_message)
        else:
            self.recording = False

    def send_message_get_answer(self, message: str) -> None:
        '''
        Send new message and get answer from chatGPT

        Args:
            message (str): message to send to chatGPT

        '''

        # print message if needed
        if self.input == 'voice':
            print(f'{CLEAR}{message.capitalize()}')

        # add message to prompt and chat history
        self.messages.append({"role": "user", "content": message})
        helpers.write_to_csv(CHAT_HISTORY_CSV, USER_NAME, message, timestamp=True)

        # print avatar feedback
        print(f'\n{CLEAR}{GREEN}{AVATAR_NAME}:{RESET}')
        print(f'{CLEAR}{GREY}(generate){RESET}', end=' ', flush=True)

        # get answer and tokens count, add it to prompt
        answer, tokens = helpers.ask_chat_gpt(messages=self.messages)
        self.prompt_tokens += tokens[0]
        self.completion_tokens += tokens[1]

        # format answer
        sentences = re.split(r"(?<=[.!?])\s", answer)
        answer = ' '.join([sentence.strip().capitalize() for sentence in sentences])

        # add answer to prompt and chat history
        self.messages.append({"role": "assistant", "content": answer})
        helpers.write_to_csv(CHAT_HISTORY_CSV, AVATAR_NAME, answer, timestamp=True)

        if self.output == 'talk':
            # generate tts
            print(f'{CLEAR}{GREY}(transcribe){RESET}', end=' ', flush=True)
            helpers.generate_tts(text=answer)

        else:
            # print answer
            print(f'{CLEAR}{answer}')

        # prompt for a new chat
        self.recording = False
        print(f'\n{RED}{USER_NAME}:{RESET}')

    def print_token_count(self) -> None:
        '''
        Print token count and price estimate
        '''

        token_price = round(self.prompt_tokens * 0.0000010 + self.completion_tokens * 0.0000020, 3)
        print(f'Tokens: Prompt {CYAN}{self.prompt_tokens}{RESET} | Completion {CYAN}{self.completion_tokens}{RESET} | Price {CYAN}${token_price}{RESET}\n')
