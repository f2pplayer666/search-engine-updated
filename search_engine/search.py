import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

data = pd.read_csv("study_knowledge_base.csv")

# ✅ combine ALL useful columns
data["combined"] = (
    data["title"] + " " +
    data["definition"] + " " +
    data["explanation"] + " " +
    data["details"] + " " +
    data["keywords"]
)

vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(data["combined"])

def ranked_search(query):

    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    best_index = scores.argmax()

    row = data.iloc[best_index]

    title = row["title"]

    # ✅ FULL DETAILED OUTPUT
    detailed = f"""
Definition:
{row['definition']}

Explanation:
{row['explanation']}

Details:
{row['details']}

Example:
{row['example']}

Key Points:
- {title} is an important concept
- It is widely used in academics

Conclusion:
This topic helps in understanding {title}.
"""

    return {
        "title": title,
        "content": detailed,
        "score": scores[best_index]
    }