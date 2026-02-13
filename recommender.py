import json
import pandas as pd
import numpy as np

from fastapi import FastAPI
from pydantic import BaseModel

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from fastapi.middleware.cors import CORSMiddleware


DATA_PATH = "movies_dataset.jsonl"   # My movies dataset

rows = []
with open(DATA_PATH, "r", encoding="utf-8") as f:
    for line in f:
        rows.append(json.loads(line))

df = pd.DataFrame(rows)

vc = df["movie_title"].value_counts()
valid_titles = vc[vc >= 2].index
df = df[df["movie_title"].isin(valid_titles)].reset_index(drop=True)

X = df[
    [
        "age",
        "gender",
        "relationship_status",
        "mood",
        "time_of_day",
        "month",
        "watch_with",
        "weather"
    ]
]

y = df["movie_title"]

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

numeric_features = ["age", "month"]
categorical_features = [
    "gender",
    "relationship_status",
    "mood",
    "time_of_day",
    "watch_with",
    "weather"
]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ]
)

model = RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

pipeline = Pipeline(
    steps=[
        ("preprocess", preprocessor),
        ("model", model)
    ]
)

# normal split (only for fitting – not needed later)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

pipeline.fit(X_train, y_train)

app = FastAPI(title="MORE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class RecommendRequest(BaseModel):
    age: int
    gender: str
    relationship_status: str
    mood: str
    time_of_day: str
    month: int
    watch_with: str
    weather: str
    top_n: int = 5


@app.post("/recommend")
def recommend(req: RecommendRequest):

    context_df = pd.DataFrame([{
        "age": req.age,
        "gender": req.gender,
        "relationship_status": req.relationship_status,
        "mood": req.mood,
        "time_of_day": req.time_of_day,
        "month": req.month,
        "watch_with": req.watch_with,
        "weather": req.weather
    }])

    probs = pipeline.predict_proba(context_df)

    top_n = min(req.top_n, probs.shape[1])

    top_idx = np.argsort(probs, axis=1)[:, -top_n:][:, ::-1][0]

    movies = label_encoder.inverse_transform(top_idx).tolist()
    scores = probs[0][top_idx].tolist()

    return {
        "recommended_movies": [
            {"movie_title": m, "score": float(s)}
            for m, s in zip(movies, scores)
        ]
    }


@app.get("/")
def root():
    return {"status": "MORE is running"}
