import hashlib
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split

# Your unique parameters
n_estimators = 80
random_state = 14
test_size = 0.2

# Load dataset and train
data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target,
    test_size=test_size,
    random_state=random_state,
)

clf = GradientBoostingClassifier(
    n_estimators=n_estimators,
    random_state=random_state,
)
clf.fit(X_train, y_train)

acc = clf.score(X_test, y_test)
print(f"Accuracy: {acc:.4f}")

# Compute verification hash
verify_input = f"n{n_estimators}:r{random_state}:acc{acc:.6f}"
verify = hashlib.sha256(verify_input.encode()).hexdigest()[:12]
print(f"Verify: {verify}")
