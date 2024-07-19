from sqlalchemy import create_engine, text
import random

db_config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'port': '3310',
    'database': 'irproject'
}

database_uri = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(database_uri)

def load_words(file_path='misc/words.txt'):
    with open(file_path, 'r') as file:
        words = file.read().splitlines()
    return words

def generate_random_text(words, min_length=5000):
    text = []
    while len(" ".join(text)) < min_length:
        text.append(random.choice(words))
    return " ".join(text)

def generate_title(words):
    return " ".join(random.sample(words, random.randint(2, 5))).title()

def create_dummy_documents(num_documents=10):
    words = load_words()
    with engine.begin() as connection:
        for i in range(num_documents):
            title = generate_title(words)
            content = generate_random_text(words)
            connection.execute(text("INSERT INTO document (title, content) VALUES (:title, :content)"),
                               {'title': title, 'content': content})
            print(f"Inserted document: {title}")

if __name__ == "__main__":
    create_dummy_documents(num_documents=30)
    print("Dummy documents created successfully.")
