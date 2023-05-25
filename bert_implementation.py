from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModel
import re
import numpy as np
from scipy.spatial.distance import cosine
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
nltk.download('stopwords')

app = Flask(__name__)
CORS(app)

tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
model = AutoModel.from_pretrained('bert-base-uncased')

def preprocess(text):
    # lowercasing and removal of stopwords
    stop_words = stopwords.words('english')
    return " ".join([word for word in text.lower().split() if word not in stop_words])

def get_sentence_embedding(sentence):
    inputs = tokenizer(sentence, return_tensors="pt")
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()[0]

def cosine_similarity(a, b):
    return 1 - cosine(a, b)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()

    query = data['query']
    text = data['text']

    # Check if the text is empty
    if not text or text.strip() == '':
        return jsonify(results=[{'text': 'No text content found on this page.', 'expandedText': 'No text content found on this page.'}])

    # Check if the query is empty
    if not query or query.strip() == '':
        return jsonify(results=[{'text': 'The search query is empty.', 'expandedText': 'The search query is empty.'}])

    sentences = text.split('.')

    results = []
    unique_texts = set()

    query_embedding = get_sentence_embedding(preprocess(query))

    for sentence in sentences:
        sentence_embedding = get_sentence_embedding(preprocess(sentence))

        similarity = cosine_similarity(query_embedding, sentence_embedding)
        words = sentence.split()

        for i in range(len(words)):
            surrounding_text = ' '.join(words[max(i - 2, 0): i + 3])
            expanded_text = ' '.join(words[max(i - 10, 0): i + 11])

            if surrounding_text.lower() not in unique_texts and similarity > 0.65:
                results.append({'text': surrounding_text, 'expandedText': expanded_text, 'similarity': similarity})
                unique_texts.add(surrounding_text.lower())

    # Sort the results by similarity and get top 5
    results.sort(key=lambda x: -x['similarity'])
    results = results[:5]

    # Remove similarity scores from results
    for result in results:
        del result['similarity']

    # Check if the query text was found
    if not results:
        return jsonify(results=[{'text': f'No instances of "{query}" found on this page.', 'expandedText': 'No instances of the search query found on this page.'}])

    return jsonify(results=results)

if __name__ == '__main__':
    print('Starting Flask server...')
    app.run(port=5000)
