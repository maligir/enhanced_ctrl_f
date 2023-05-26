from flask import Flask, request, jsonify
from flask_cors import CORS
import re, string
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

app = Flask(__name__)
CORS(app)

model_name = "deepset/roberta-base-squad2"
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()

    query = data['query']
    text = data['text']

    if not text or text.strip() == '':
        return jsonify(results=[{'text': 'No text content found on this page.', 'expandedText': 'No text content found on this page.'}])

    if not query or query.strip() == '':
        return jsonify(results=[{'text': 'The search query is empty.', 'expandedText': 'The search query is empty.'}])

    # text = preprocess_text(text)
    
    results = []
    answers = nlp({'question': query, 'context': text})  # Get top 5 answers
    results.append({'text': answers['answer'] if len(answers['answer']) < 100 else answers['answer'][:100], 'expandedText': answers['answer']})
    
    if not answers:
        return jsonify(results=[{'text': 'No answers found.', 'expandedText': 'No answers found.'}])

    print(answers)

    return jsonify(results=results)

if __name__ == '__main__':
    print('Starting Flask server...')
    app.run(port=5000)
