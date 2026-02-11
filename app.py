from flask import Flask, render_template, request
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
from gtts import gTTS
import os

app = Flask(__name__)

# Load model once
nlp = spacy.load('en_core_web_sm')

# Ensure static folder exists
if not os.path.exists("static"):
    os.makedirs("static")


def summarizer(rawdocs):
    stopwords = list(STOP_WORDS)
    doc = nlp(rawdocs)

    word_freq = {}
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            if word.text not in word_freq:
                word_freq[word.text] = 1
            else:
                word_freq[word.text] += 1

    if len(word_freq) == 0:
        return "", doc, 0, 0

    max_freq = max(word_freq.values())

    for word in word_freq.keys():
        word_freq[word] = word_freq[word] / max_freq

    sent_tokens = [sent for sent in doc.sents]

    sent_scores = {}
    for sent in sent_tokens:
        for word in sent:
            if word.text in word_freq:
                if sent not in sent_scores:
                    sent_scores[sent] = word_freq[word.text]
                else:
                    sent_scores[sent] += word_freq[word.text]

    select_len = max(1, int(len(sent_tokens) * 0.3))

    summary_sentences = nlargest(select_len, sent_scores, key=sent_scores.get)
    final_summary = [sent.text for sent in summary_sentences]
    summary = ' '.join(final_summary)

    return summary, doc, len(rawdocs.split()), len(summary.split())


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    rawtext = request.form['input_text']
    summary, doc, original_len, summary_len = summarizer(rawtext)

    audio_file = None

    if summary.strip() != "":
        # 🎧 Convert summary to audio
        tts = gTTS(text=summary, lang='ur')
        audio_path = os.path.join("static", "summary_audio.mp3")
        tts.save(audio_path)
        audio_file = "summary_audio.mp3"

    return render_template('index.html',
                           summary=summary,
                           original_len=original_len,
                           summary_len=summary_len,
                           audio_file=audio_file)


if __name__ == '__main__':
    app.run(debug=True)
