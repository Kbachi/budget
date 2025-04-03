from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import chatbot

app = Flask(__name__, static_folder='static', template_folder='.')
CORS(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/saym')
def saym():
    return render_template('saym.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    print("Received message from client:", user_message)  # Debug log
    
    reply = chatbot.get_response(user_message)
    print("Reply from chatbot:", reply)  # Debug log
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)