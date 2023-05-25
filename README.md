
# Enhanced CTRL_F: Webpage Text Analysis with Chrome Extension, Flask, and Machine Learning

This project is about creating a Chrome extension that uses Flask as a backend for processing webpage text. The Flask server also incorporates a Machine Learning model to process user queries and returns the most relevant sections of the webpage text. We implement this using two methods: simple Natural Language Processing (NLP) and BERT-based NLP.

## Setup

### Chrome Extension

The Chrome extension code is mainly located in `popup.js`. This file includes code to handle the user interface and interaction, such as entering search queries and toggling dark mode.

To install the Chrome extension, follow these steps:

1. Open Google Chrome and navigate to `chrome://extensions`.
2. Enable Developer Mode by clicking the toggle switch at the top right.
3. Click the 'Load Unpacked' button and select the directory containing `manifest.json` and `popup.js`.

### Flask Server

The Flask server is located in `app.py`. It handles POST requests from the Chrome extension, processes the webpage text, and uses a Machine Learning model to find the most relevant sections of text based on the user's query.

To set up the Flask server, follow these steps:

1. Install Python 3.7 or later.
2. Install the necessary packages with `pip install flask flask_cors transformers sklearn numpy nltk` or `pip install -r requirements.txt`.
3. Run the server with `python app.py` or `bert_implementation.py`.

## Machine Learning Models

We use two different models to process the user's query and find relevant sections of text: a simple NLP model and a BERT-based model.

### Simple NLP Model

The simple NLP model uses basic text processing techniques like tokenization and stemming to process the text and the user's query. It then uses cosine similarity to find the sections of text that are most similar to the query.

### BERT-Based Model

The BERT-based model uses a pre-trained BERT model to convert the text and the user's query into vector embeddings. It then uses cosine similarity to find the sections of text that are most similar to the query. The BERT-based model generally achieves better results, especially for more complex queries, but it also requires more computational resources.

To use the BERT-based model, additional setup is needed:

1. Install the transformers package with `pip install transformers`.
2. Download the pre-trained BERT model with `python -c "from transformers import BertModel, BertTokenizer; BertModel.from_pretrained('bert-base-uncased'); BertTokenizer.from_pretrained('bert-base-uncased')"`.

For each of these implementations, the Flask server receives the user's query and the webpage text, processes the text using the chosen model, and then sends back the top 5 sections of text based on their similarity to the query.

## Limitations and Future Work

Both models have limitations, and there are many ways the project could be extended. For example, the simple NLP model does not handle semantic similarity very well, while the BERT model might require too much computational power for some systems. Future work could explore using different models, such as RoBERTa or ELECTRA, and implementing additional features like automatic question-answering or summarization.

## Acknowledgements

This project uses code from the Flask, transformers, and NLTK libraries. It also uses the BERT pre-trained model from Hugging Face.
