import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

data = pd.read_csv("study_knowledge_base.csv")
data["combined"] = data["title"] + " " + data["summary"]

vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(data["combined"])

def ranked_search(query):

    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    best_index = scores.argmax()

    title = data.iloc[best_index]["title"]
    content = data.iloc[best_index]["summary"]

    detailed = f"""
{content}

Explanation:
{content}

Key Points:
- {title} is an important concept
- It is widely used in studies

Conclusion:
This topic helps in understanding {title}.
"""

    return {
        "title": title,
        "content": detailed,
        "score": scores[best_index]
    }