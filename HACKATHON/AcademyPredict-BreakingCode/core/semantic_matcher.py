from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords", quiet=True)

STOPWORDS_ES = stopwords.words("spanish")

def recomendar_areas(perfil_texto, df_areas, top_k=5):
    corpus = [perfil_texto] + df_areas["texto_area"].astype(str).tolist()

    vectorizer = TfidfVectorizer(
        stop_words=STOPWORDS_ES,
        ngram_range=(1, 2),
        min_df=1
    )

    X = vectorizer.fit_transform(corpus)

    perfil_vec = X[0]
    areas_vecs = X[1:]

    scores = (areas_vecs @ perfil_vec.T).toarray().ravel()

    df_areas = df_areas.copy()
    df_areas["afinidad"] = scores / scores.max() * 0.95 if scores.max() > 0 else 0

    return df_areas.sort_values("afinidad", ascending=False).head(top_k)