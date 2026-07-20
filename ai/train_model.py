import re
import joblib
import pandas as pd

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# -------------------------
# Load Dataset
# -------------------------

df = pd.read_csv("ai/dataset/hostel_complaints_v2_1000.csv")

# -------------------------
# Merge title + description
# -------------------------

df["text"] = df["title"] + " " + df["description"]

# -------------------------
# NLP Preprocessing
# -------------------------

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess(text):

    text = text.lower()

    text = re.sub(r"[^a-zA-Z ]", " ", text)

    words = text.split()

    words = [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in stop_words
    ]

    return " ".join(words)

df["text"] = df["text"].apply(preprocess)

# -------------------------
# Features
# -------------------------

X = df["text"]

y = df["priority"]

# -------------------------
# Train Test Split
# -------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -------------------------
# TF-IDF
# -------------------------

vectorizer = TfidfVectorizer(
    ngram_range=(1,2),
    min_df=2,
    max_df=0.95
)

X_train = vectorizer.fit_transform(X_train)

X_test = vectorizer.transform(X_test)

# -------------------------
# Linear SVM
# -------------------------

model = LinearSVC()

model.fit(X_train, y_train)

# -------------------------
# Prediction
# -------------------------

pred = model.predict(X_test)

# -------------------------
# Evaluation
# -------------------------

print("\nAccuracy\n")
print(accuracy_score(y_test,pred))

print("\nClassification Report\n")
print(classification_report(y_test,pred))

print("\nConfusion Matrix\n")
print(confusion_matrix(y_test,pred))

# -------------------------
# Save Model
# -------------------------

joblib.dump(model,"ai/models/model.pkl")
joblib.dump(vectorizer,"ai/models/vectorizer.pkl")

print("\nModel Saved Successfully")