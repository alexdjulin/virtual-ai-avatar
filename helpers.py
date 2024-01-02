from openai import OpenAI
from dotenv import dotenv_values
from tenacity import retry, wait_random_exponential, stop_after_attempt
import csv

EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-3.5-turbo"


def get_openai_client():
    '''Create client instance'''
    return OpenAI(api_key=dotenv_values()["OPENAI_API_KEY"])


def ask_chat_gpt(messages: str, model: str = GPT_MODEL):
    ''' Create client instance and return chat response '''

    client = get_openai_client()
    completion = client.chat.completions.create(model=model, messages=messages)
    answer = completion.choices[0].message.content
    return answer


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_embeddings(answer: str, model: str = EMBEDDING_MODEL) -> None:
    '''Generate embeddings for an input string'''

    client = get_openai_client()
    answer = answer.replace("\n", " ")  # replace newlines
    return client.Embedding.create(input=answer, model=model)["data"][0]["embedding"]


def load_from_csv(csvfile: str) -> dict:
    '''Loads contents from csv file into a qna dict'''

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
    '''Write contents of a qna dict to a csv file'''

    try:
        with open(csvfile, 'a', newline='') as csvfile:
            fieldnames = ['Question', 'Answer']
            writer = csv.DictWriter(csvfile, quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
            for question, answer in qna_dict.items():
                writer.writerow({'Question': question, 'Answer': answer})

    except Exception as e:
        print(f"Error writing to CSV file: {e}")