import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Load and preprocess data
df = pd.read_csv('network_traffic.csv')
df = df.dropna()

# Adding a 'label' column for demonstration
# 0 = legitimate user, 1 = intruder
# This should be based on actual data analysis or domain knowledge
df['label'] = [0 if x % 2 == 0 else 1 for x in range(len(df))]  # Example: alternating labels

# Feature scaling
scaler = StandardScaler()
features = ['packet_size', 'total_packets', 'total_bytes', 'flow_duration']
df[features] = scaler.fit_transform(df[features])

# Define features and target variable
X = df[features]
y = df['label']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print(classification_report(y_test, y_pred))
