import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('./combined_dataset.csv')
print("Loaded dataset")

# Specify the features (X) and the target variable (y)
X = df.drop('x', axis=1)  # Features (all columns except the target_column)
y = df['x']  # Target variable

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=35)

# Scale data
scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

# Perform PCA
pca = PCA(n_components=0.85)
pca.fit(X_train)
X_train = pca.transform(X_train)
X_test = pca.transform(X_test)
print("PCA completed")

print("Number of columns in X_train:", X_train.shape[1])
print("Number of columns in X_test:", X_test.shape[1])
print(pd.DataFrame(X_train[:1], columns=[f'PC{i}' for i in range(1, X_train.shape[1] + 1)]))

# Print explained variance
explained_variance = pca.explained_variance_ratio_
print("Explained variance:")
print(explained_variance)

# Create an XGBoost classifier
xgboost_classifier = XGBClassifier(n_estimators=100, random_state=35)

# Train the classifier
print("Training the model....")
xgboost_classifier.fit(X_train, y_train)
print("Training completed")

# Make predictions on the testing data
y_pred = xgboost_classifier.predict(X_test)
print("Making predictions...")

# Print the metrics
print("Printing metrics...")
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy}')

conf_matrix = confusion_matrix(y_test, y_pred)
print('Confusion Matrix:\n', conf_matrix)

plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.savefig('confusion_matrix_plot_xgb.png')

classification_rep = classification_report(y_test, y_pred)
print('Classification Report:\n', classification_rep)
