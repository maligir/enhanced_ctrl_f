from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from typing import Dict, List, Tuple

app = Flask(__name__)
CORS(app)

model_name = "distilbert-base-uncased-distilled-squad"
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)
model = SentenceTransformer('stsb-roberta-large')
results = []

import re

def find_instances(text, query):
    result = []
    words = text.split()
    regex = re.compile(r'\b' + re.escape(query) + r'\b', re.I)  # \b for word boundary, re.I for case-insensitive

    for i in range(len(words)):
        if regex.search(words[i]):
            start = max(0, i - 5)  # 5 words before
            end = min(len(words), i + 6)  # 5 words after
            surrounding_text = ' '.join(words[start:end])
            start = max(0, i - 10)  # 10 words before
            end = min(len(words), i + 11)  # 10 words after
            expanded_text = ' '.join(words[start:end])
            result.append({'text': surrounding_text + "...", 'expandedText': expanded_text})
            
    if len(result) == 0:
        result.append({'text': 'No exact matches found.', 'expandedText': 'No exact matches found. The search query was not found in the text. Try searching for a different query or view other context based suggestions by clicking back.'})
    return result

def first_n_words(sentence: str, n: int) -> str:
    words = sentence.split()
    if len(words) < n:
        return sentence + "."  # return the whole sentence if it has less than 'n' words
    return ' '.join(words[:n]) + '...'  # return the first 'n' words followed by '...'

def find_context(query, text):
    result = []
    sentences = text.split('.')
    sentences = list(set(filter(None, sentences)))
    sentences.append(query)
    embeddings = model.encode(sentences, convert_to_tensor=True)
    
    # Compute cosine-similarities for each sentence with the query sentence
    similarity = [(sentence, util.pytorch_cos_sim(embeddings[i], embeddings[-1]).item())
                for i, sentence in enumerate(sentences)]

    # Sort the results by the similarity score in descending order
    similarity.sort(key=lambda x: x[1], reverse=True)

    # Get the top 5 most similar sentences
    top_5_sentences: List[Tuple[str, float]] = similarity[1:6]  # start from 1 to exclude the query itself
    
    # Append the top 5 sentences to the existing 'result' list
    for sentence, _ in top_5_sentences:
        result.append({'text': first_n_words(sentence, 10), 'expandedText': sentence + "."})

    return result

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data['query']
    text = data['text']
    if not text or text.strip() == '':
        return jsonify(results=[{'text': 'No text content found on this page.', 'expandedText': 'No text content found on this page.'}])
    if not query or query.strip() == '':
        return jsonify(results=[{'text': 'The search query is empty.', 'expandedText': 'The search query is empty.'}])
    results = []
    
    # find answer to question
    answers = nlp({'question': query, 'context': text})
    if (not answers) or (answers['score'] < 0.2):
        results.append({'text': 'No answers found.', 'expandedText': 'No answers found. The answers that were generated were not confident enough: ' + str(round(answers['score'] * 100)) + '%'})
    else:
        results.append({'text': answers['answer'] if len(answers['answer']) < 100 else answers['answer'][:100], 'expandedText': answers['answer'] + ' <br><br>(This answer is ' + str(round(answers['score'] * 100)) + '% confident)'})
    
    # find contextual instances of query
    results.extend(find_context(query, text))
        
    # find exact matches
    results.extend(find_instances(text, query))
    
    return jsonify(results=results)

if __name__ == '__main__':
    print('Starting Flask server...')
    app.run(port=5000)
