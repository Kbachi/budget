from flask import Flask, request, jsonify, render_template
import chatbot  # This is your chatbot.py module
from chatbot import get_response

app = Flask(__name__, static_folder='static', template_folder='.')
# If you plan to serve your pages on the same domain, use the above setup.
# Alternatively, adjust the static/template folder paths as needed.

@app.route('/')
def home():
    return render_template('home.html')  # Your home page

@app.route('/saym')
def saym():
    return render_template('saym.html')  # This is the page with our chat interface

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    reply = chatbot.get_response(user_message)
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)
