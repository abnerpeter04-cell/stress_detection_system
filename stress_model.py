import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Sample dataset
data = {
    'study_hours': [2, 8, 7, 1, 6, 5, 9, 3],
    'sleep_hours': [8, 3, 4, 9, 5, 6, 2, 8],
    'break_frequency': [5, 1, 2, 6, 2, 3, 1, 5],
    'stress': [0, 1, 1, 0, 1, 0, 1, 0]
}

df = pd.DataFrame(data)

X = df[['study_hours', 'sleep_hours', 'break_frequency']]
y = df['stress']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier()
model.fit(X_train, y_train)

joblib.dump(model, 'model.pkl')

print("Model trained and saved.")