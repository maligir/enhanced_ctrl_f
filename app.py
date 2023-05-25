from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()

    query = data['query']
    text = data['text']

    # Check if the text is empty
    if not text or text.strip() == '':
        return jsonify(error='No text content found on this page.'), 400

    # Check if the query is empty
    if not query or query.strip() == '':
        return jsonify(error='The search query is empty.'), 400

    escaped_query = re.escape(query)  # Escapes special characters for regex
    regex = re.compile('\\b' + escaped_query + '\\b', re.I)  # Case insensitive
    words = text.split()

    results = []
    for i in range(len(words)):
        if regex.search(words[i]):
            surrounding_text = ' '.join(words[max(i - 2, 0): i + 3])
            expanded_text = ' '.join(words[max(i - 10, 0): i + 11])
            results.append({'text': surrounding_text, 'expandedText': expanded_text})
            
    # Check if the query text was found
    if not results:
        return jsonify(error=f'No instances of "{query}" found on this page.'), 400

    return jsonify(results=results)

if __name__ == '__main__':
    print('Starting Flask server...')
    app.run(port=5000)
