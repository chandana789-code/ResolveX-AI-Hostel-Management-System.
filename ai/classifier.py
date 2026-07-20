import joblib
import re

model = joblib.load("ai/models/model.pkl")
vectorizer = joblib.load("ai/models/vectorizer.pkl")


def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def predict_priority(title, description):

    text = title + " " + description

    text = clean_text(text)

    vector = vectorizer.transform([text])

    prediction = model.predict(vector)

    return prediction[0]