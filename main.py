from flask import Flask, jsonify
from flask import request
import json
from flask_cors import CORS
from transformers import T5ForConditionalGeneration, T5Tokenizer, AdamW
from torch.utils.data import DataLoader, Dataset
import torch
import psycopg2
import random



app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# load model into memory
# Load T5 tokenizer and model for conditional generation
model_name = 't5-small'
tokenizer = T5Tokenizer.from_pretrained("C:\\Users\\Yasho Nandan Reddy\\Downloads\\recipe")
model = T5ForConditionalGeneration.from_pretrained("C:\\Users\\Yasho Nandan Reddy\\Downloads\\recipe")
# user="default"
# database= "verceldb"
# password= "1HURNrWk6zfm"
# host= "ep-divine-frog-a1m53t5a-pooler.ap-southeast-1.aws.neon.tech"
# connectionString= "postgres://default:1HURNrWk6zfm@ep-divine-frog-a1m53t5a-pooler.ap-southeast-1.aws.neon.tech:5432/verceldb?sslmode=require"

# conn = psycopg2.connect(f"dbname={database} user={user} password={password} host={host} port={5432}")
# cur = conn.cursor()
# data = (1, "nandu", "synrreddy@gmail.com", "synr752004")

# # Execute the command
# cur.execute('INSERT INTO users (id, username, email, password) VALUES (%s, %s, %s, %s)', data)

# # Commit the changes and close the connection
# conn.commit()
# cur.close()
# conn.close()

def insert_user_data( username, email, password):
    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="verceldb",
            user="default",
            password="1HURNrWk6zfm",
            host="ep-divine-frog-a1m53t5a-pooler.ap-southeast-1.aws.neon.tech",
            port=5432
        )
        
        # Create a cursor object to execute SQL queries
        cur = conn.cursor()

        # Execute the INSERT command
        cur.execute('INSERT INTO users ( username, email, password) VALUES ( %s, %s, %s)', ( username, email, password))

        # Commit the transaction
        conn.commit()

        # Close the cursor and connection
        cur.close()
        conn.close()

        return True, None  # Success
    except Exception as e:
        return False, str(e)  # Failure with error message

# API endpoint to handle user registration
@app.route('/Register', methods=['POST'])
def register_user():
    # Parse request data
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Insert user data into the database
    success, error_message = insert_user_data( username, email, password)

    if success:
        return jsonify({'success': True, 'message': 'User registered successfully'}), 200
    else:
        return jsonify({'success': False, 'error': error_message}), 500
    


# Function to verify user credentials for sign-in
def verify_user_credentials(email, password):
    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="verceldb",
            user="default",
            password="1HURNrWk6zfm",
            host="ep-divine-frog-a1m53t5a-pooler.ap-southeast-1.aws.neon.tech",
            port=5432
        )
        
        # Create a cursor object to execute SQL queries
        cur = conn.cursor()

        # Execute a SELECT query to fetch user data
        cur.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        user_data = cur.fetchone()

        # Close the cursor and connection
        cur.close()
        conn.close()

        if user_data:
            return True, None  # Credentials verified successfully
        else:
            return False, "Incorrect email or password"  # Invalid credentials
    except Exception as e:
        return False, str(e)  # Failure with error message

# API endpoint to handle user sign-in
@app.route('/Signin', methods=['POST'])
def login_user():
    # Parse request data
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Verify user credentials
    success, error_message = verify_user_credentials(email, password)

    if success:
        return jsonify({'success': True, 'message': 'User signed in successfully'}), 200
    else:
        return jsonify({'success': False, 'error': error_message}), 401



def generate_text(prompt):
    input_text = f"question: {prompt} "

    # Tokenize input
    input_ids = tokenizer.encode(input_text, return_tensors='pt', truncation=True, padding='max_length', max_length=1024)

    # Generate answer
    output_ids = model.generate(input_ids , max_length = 1024)

    # Decode the answer from token ids
    answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    return answer

# Array of responses for greetings
GREETINGS_RESPONSES = ["Hi! How can I assist?", "Hello! How can I assist?", "Hey there! How can I assist?"]

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the text string from the request body
        input_string = request.data.decode('utf-8').lower()

        # Check for greetings
        if input_string.strip() in ["hi", "hello", "hey"]:
            # Return a random response from the array
            response_text = random.choice(GREETINGS_RESPONSES)
        else:
            # Generate the output string using the model
            output_string = generate_text(input_string)
            response_text = output_string
        
        # Return the response with CORS headers
        response = jsonify(output=response_text)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


if __name__ == '__main__':
    app.run(debug=True)