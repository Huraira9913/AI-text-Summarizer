import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
from gtts import gTTS   # 👈 NEW IMPORT

text = """Samsung is a South Korean multinational technology company founded in 1938. It is one of the world’s largest manufacturers of 
smartphones, televisions, semiconductors, and consumer electronics. Samsung is especially known for its Galaxy smartphone series and 
innovative advancements in display technology, memory chips, and home appliances. The company plays a major role in the global 
electronics industry through continuous innovation, research, and development."""

def summarizer(rawdocs):

    stopwords = list(STOP_WORDS)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(rawdocs)

    word_freq = {}
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            if word.text not in word_freq:
                word_freq[word.text] = 1
            else:
                word_freq[word.text] += 1

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

    select_len = max(1, int(len(sent_tokens) * 0.3))  # 👈 safety added

    summary = nlargest(select_len, sent_scores, key=sent_scores.get)

    final_summary = [sent.text for sent in summary]
    summary_text = ' '.join(final_summary)

    return summary_text


# 🔥 Generate Summary
summary = summarizer(text)

print("Summary:\n", summary)


# 🎧 Convert Summary to Audio
tts = gTTS(text=summary, lang='en')
tts.save("summary_audio.mp3")

print("\nAudio file 'summary_audio.mp3' created successfully!")
