import helpers
from cache import Cache

INTERLOCUTOR = 'Bob'
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"
CSV_FILE = "answers.csv"


class AiAvatar:
    '''Class to generate the avatar backstory and chat with him'''

    def __init__(self):
        '''Create class instance'''

        self.story_dict = {}
        self.blacklist = []
        self.embeddings = {}
        self.embedding_cache = Cache()
        self.load_story()

    def __repr__(self):
        '''Prints questions, answers and blacklist'''

        result = ''
        separator = 200 * '-' + '\n'

        # prints questions and answers
        if self.story_dict:
            result += f'{separator}## QUESTIONS / ANSWERS\n{separator}'
            id = 1
            for q, a in self.story_dict.items():
                result += f'{id}. {q} >> {a}\n'
                id += 1

        # prints blacklisted questions
        if self.blacklist:
            result += f'{separator}## BLACKLISTED QUESTIONS\n{separator}'
            id = 1
            for q in self.blacklist:
                result += f'{id}. {q}\n'
                id += 1

        return result

    def load_story(self, csvfile: str = CSV_FILE) -> None:
        '''Loads avatar story from csv file'''

        try:
            qna_dict = helpers.load_from_csv(csvfile)
            for question, answer in qna_dict.items():
                if answer == 'BLACKLIST':
                    # add question to blacklist
                    self.blacklist.append(question)
                else:
                    # store question/answer
                    self.story_dict[question] = answer

        except Exception as e:
            print(f"Error loading avatar story: {e}")

    def create_backstory(self, subject: str = 'general inquiries', questions: int = 5) -> None:
        '''
        Build avatar backstory by answering questions from chatGPT about him
        Generate embeddings to group information together
        Save answers to csv and embeddings to cache
        '''

        for _ in range(questions):

            # generate prompt including list of given answers and blacklist
            messages = [
            {
                'role': 'system',
                'content': f"""
                You are writing the autobiography of your interlocutor and you need to know everything about him.
                [Directives:
                - Limit your questions to the following subject: {subject}.
                - Here are some information you already know about him: {list(self.story_dict.values())}.
                - Don't ask a question if you already know the answer.
                - Don't ask questions from this black list: {self.blacklist}.
                - Limit your answers to one single question.
                - Be direct but friendly.]
                """
            },
            {
                "role": "user",
                "content": f"Ask me something you don't know about me?"
            },
            ]

            try:
                question = helpers.ask_chat_gpt(messages=messages)
                print(f'chatGPT: {question}')
                answer = input('Alex: ')

                if answer.lower() in {'', 'pass', 'skip'}:
                    # blacklist question
                    self.blacklist.append(question)
                    answer = 'BLACKLIST'

                elif answer.lower() in {'quit', 'exit'}:
                    # exit program
                    break

                # else:
                    # store answer and generate embeddings
                    # self.embedding_cache[answer] = get_embedding(answer)

                # add question/answer to csv
                self.story_dict[question] = answer
                helpers.write_to_csv(CSV_FILE, {question: answer})

            except Exception as error:
                print(f"Error generating question: {error}")

        print('Done asking questions')


    def chat_with_avatar(self) -> None:
        '''Chat with the avatar'''

        print('# Chat Begin #')
        # generate prompt including list of given answers and blacklist
        messages = [
            {
                'role': 'system',
                'content': f"""
                You are having a friendly conversatoin with your interlocutor.
                You both want to know more about each other.
                [Directives:
                - Here are some information about you that you can use to answer your interlocutor's questions: {list(self.story_dict.values())}.
                - Be friendly, keep the conversation going by answering as best as you can.
                - If you don't know an answer, just make one up that fits your back story.]
                """
            }]

        while True:
            try:
                prompt = input('Alex: ')
                if prompt.lower() in {'quit', 'exit'}:
                    # exit program
                    break
                messages.append({"role": "user", "content": prompt})
                answer = helpers.ask_chat_gpt(messages=messages)
                print(f'chatGPT: {answer}')
                messages.append({"role": "assistant", "content": answer})

            except Exception as error:
                print(f"Error getting answer from chatGPT: {error}")

        print('# CHAT END #')