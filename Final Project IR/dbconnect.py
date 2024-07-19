from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

db_config = {
    'user': 'root',
    'password': 'password',
    'host': 'localhost',
    'port': 'xxxx',  # Specify the port
    'database': 'irproject'
}

# Create a SQLAlchemy database URI
database_uri = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

# Use this URI in your Flask app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

def create_index_if_not_exists(connection, index_name, table_name, index_query):
    try:
        result = connection.execute(text(f"SHOW INDEX FROM {table_name} WHERE Key_name = '{index_name}';"))
        if not result.fetchone():
            connection.execute(text(index_query))
    except Exception as e:
        print(f"Error checking/creating index {index_name} on {table_name}: {e}")

# Ensure the tables are created
with app.app_context():
    try:
        db.create_all()
        with db.engine.connect() as connection:
            # Adding indexes if they do not exist
            create_index_if_not_exists(connection, 'idx_username', 'user', 'CREATE INDEX idx_username ON user(username);')
            create_index_if_not_exists(connection, 'idx_email', 'user', 'CREATE INDEX idx_email ON user(email);')
            create_index_if_not_exists(connection, 'idx_content_title', 'document', 'CREATE FULLTEXT INDEX idx_content_title ON document(content, title);')
        print("Tables and indexes created successfully")
    except Exception as e:
        print(f"Error creating tables or indexes: {e}")
