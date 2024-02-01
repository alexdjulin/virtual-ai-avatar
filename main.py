import os
from ai_avatar import AiAvatar
from logger import get_logger
import argparse
from terminal import CYAN, RESET

# create logger
LOG = get_logger(os.path.splitext(os.path.basename(__file__))[0])

# add arguments to specify input and output methods in chat mode
parser = argparse.ArgumentParser(description='Chose input / output methods to chat with Avatar')
parser.add_argument('--input', '-i', type=str, default=None, help='Input method')
parser.add_argument('--output', '-o', type=str, default=None, help='Output method')
args = parser.parse_args()


if __name__ == '__main__':

    # create avatar instance
    avatar = AiAvatar()

    # start chat mode if arguments are provided
    if args.input or args.output:
        avatar.chat_with_avatar(input_method=args.input, output_method=args.output)

    else:
        print(f'\n{CYAN}# SELECT MODE #{RESET}')
        choice = input(f'{CYAN}1.{RESET} Create Avatar Story\n{CYAN}2.{RESET} Chat with Avatar\n>> ')

        while not choice in {'', '1', '2'}:
            choice = input('>> ')

        if choice == '1':
            # create avatar story mode
            LOG.info('Create Avatar Story mode selected')
            avatar.create_avatar_story()

        elif choice == '2':
            # chat with avatar mode
            LOG.info('Chat With Avatar mode selected')
            avatar.chat_with_avatar()

