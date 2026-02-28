from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

vectorizer = TfidfVectorizer()
model = LogisticRegression()

training_data = [
    "python tensorflow deep learning nlp",
    "react html css javascript",
    "aws docker kubernetes ci cd"
]

labels = ["AI Engineer", "Frontend Developer", "DevOps Engineer"]

X = vectorizer.fit_transform(training_data)
model.fit(X, labels)

def classify_role(text):
    X_test = vectorizer.transform([text])
    return model.predict(X_test)[0]