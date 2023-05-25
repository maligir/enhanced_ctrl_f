from flask import Flask, request, jsonify
from flask_cors import CORS
import re, string
from transformers import pipeline

import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('stopwords')
from nltk.corpus import stopwords

app = Flask(__name__)
CORS(app)

nlp = pipeline('question-answering')  # Initialize the question-answering pipeline

def preprocess_text(text):
    text = text.lower()  # Convert text to lower case
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    stop_words = set(stopwords.words('english'))  # Remove stopwords
    words = text.split()
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()

    query = data['query']
    text = data['text']

    if not text or text.strip() == '':
        return jsonify(results=[{'text': 'No text content found on this page.', 'expandedText': 'No text content found on this page.'}])

    if not query or query.strip() == '':
        return jsonify(results=[{'text': 'The search query is empty.', 'expandedText': 'The search query is empty.'}])

    text = preprocess_text(text)
    
    results = []
    answers = nlp(question=query, context=text, topk=5)  # Get top 5 answers
    
    if not answers:
        return jsonify(results=[{'text': 'No answers found.', 'expandedText': 'No answers found.'}])

    for ans in answers:
        start = max(0, ans['start'] - 20)
        end = min(len(text), ans['end'] + 20)
        results.append({
            'text': ans['answer'],
            'expandedText': text[start:end],
        })

    return jsonify(results=results)

if __name__ == '__main__':
    print('Starting Flask server...')
    app.run(port=5000)
