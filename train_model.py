import os
import re
import random
import string
import pickle

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# ==============================
# SETTINGS
# ==============================

random.seed(42)
np.random.seed(42)

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)


# ==============================
# PASSWORD LISTS
# ==============================

common_passwords = [
    "password",
    "password123",
    "123456",
    "12345678",
    "123456789",
    "qwerty",
    "qwerty123",
    "admin",
    "admin123",
    "welcome",
    "welcome123",
    "letmein",
    "abc123",
    "iloveyou",
    "monkey",
    "dragon",
    "football",
    "login",
    "user123",
    "india123"
]

names = [
    "rahul",
    "prashant",
    "rohit",
    "amit",
    "ankit",
    "neha",
    "pooja",
    "sneha",
    "arjun",
    "vikas"
]

words = [
    "cloud",
    "python",
    "data",
    "science",
    "secure",
    "security",
    "computer",
    "analytics",
    "developer",
    "machine",
    "learning",
    "database",
    "technology"
]


# ==============================
# PASSWORD GENERATORS
# ==============================

def generate_weak_password():

    options = [
        random.choice(common_passwords),
        random.choice(names) + str(random.randint(1, 999)),
        random.choice(words),
        random.choice(words) + str(random.randint(1, 999)),
        "123456" + random.choice(string.digits)
    ]

    return random.choice(options)


def generate_medium_password():

    base = random.choice(words + names)

    options = [
        base.capitalize() + str(random.randint(10, 9999)),
        base + str(random.randint(1000, 99999)),
        base.capitalize() + "@" + str(random.randint(10, 999)),
        base + random.choice(["!", "@", "#", "$"]) +
        str(random.randint(10, 999))
    ]

    return random.choice(options)


def generate_strong_password():

    length = random.randint(12, 18)

    characters = (
        string.ascii_letters +
        string.digits +
        "!@#$%^&*"
    )

    return "".join(
        random.choice(characters)
        for _ in range(length)
    )


# ==============================
# DATASET GENERATION
# ==============================

def generate_dataset(n=10000):

    passwords = []
    labels = []

    for _ in range(n):

        category = random.choice([
            "weak",
            "weak",
            "medium",
            "medium",
            "strong"
        ])

        if category == "weak":

            password = generate_weak_password()
            label = 0

        elif category == "medium":

            password = generate_medium_password()
            label = 1

        else:

            password = generate_strong_password()
            label = 2

        passwords.append(password)
        labels.append(label)

    return pd.DataFrame({
        "password": passwords,
        "strength": labels
    })


df = generate_dataset()

df.to_csv(
    "data/password_dataset.csv",
    index=False
)

print("Dataset created successfully.")


# ==============================
# FEATURE ENGINEERING
# ==============================

common_set = set(
    p.lower()
    for p in common_passwords
)


def calculate_entropy(password):

    pool = 0

    if re.search(r"[a-z]", password):
        pool += 26

    if re.search(r"[A-Z]", password):
        pool += 26

    if re.search(r"[0-9]", password):
        pool += 10

    if re.search(r"[^a-zA-Z0-9]", password):
        pool += 32

    if pool == 0:
        return 0

    return len(password) * np.log2(pool)


def repeated_character_count(password):

    count = 0

    for i in range(len(password) - 1):

        if password[i] == password[i + 1]:
            count += 1

    return count


def has_sequence(password):

    sequences = [
        "123",
        "234",
        "345",
        "456",
        "567",
        "678",
        "789",
        "abc",
        "bcd",
        "qwe"
    ]

    password = password.lower()

    for seq in sequences:

        if seq in password:
            return 1

    return 0


def extract_features(password):

    length = len(password)

    lowercase_count = sum(
        c.islower()
        for c in password
    )

    uppercase_count = sum(
        c.isupper()
        for c in password
    )

    digit_count = sum(
        c.isdigit()
        for c in password
    )

    special_count = sum(
        not c.isalnum()
        for c in password
    )

    unique_chars = len(set(password))

    entropy = calculate_entropy(password)

    repeated_chars = repeated_character_count(password)

    common_password = int(
        password.lower() in common_set
    )

    sequence_flag = has_sequence(password)

    digit_ratio = digit_count / max(length, 1)

    special_ratio = special_count / max(length, 1)

    unique_ratio = unique_chars / max(length, 1)

    return [
        length,
        lowercase_count,
        uppercase_count,
        digit_count,
        special_count,
        unique_chars,
        entropy,
        repeated_chars,
        common_password,
        sequence_flag,
        digit_ratio,
        special_ratio,
        unique_ratio
    ]


feature_names = [
    "length",
    "lowercase_count",
    "uppercase_count",
    "digit_count",
    "special_count",
    "unique_chars",
    "entropy",
    "repeated_chars",
    "common_password",
    "has_sequence",
    "digit_ratio",
    "special_ratio",
    "unique_ratio"
]


X = pd.DataFrame(
    df["password"]
    .apply(extract_features)
    .tolist(),
    columns=feature_names
)

y = df["strength"]


# ==============================
# TRAIN TEST SPLIT
# ==============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ==============================
# RANDOM FOREST MODEL
# ==============================

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=18,
    random_state=42,
    class_weight="balanced"
)

model.fit(
    X_train,
    y_train
)


# ==============================
# MODEL EVALUATION
# ==============================

y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print()
print("==============================")
print("MODEL PERFORMANCE")
print("==============================")

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)

print()
print("Classification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Weak",
            "Medium",
            "Strong"
        ]
    )
)


# ==============================
# SAVE MODEL
# ==============================

model_package = {

    "model": model,

    "features": feature_names,

    "accuracy": accuracy,

    "classes": [
        "Weak",
        "Medium",
        "Strong"
    ]
}


with open(
    "models/password_strength_model.pkl",
    "wb"
) as file:

    pickle.dump(
        model_package,
        file
    )


print()
print("Model saved successfully!")
print(
    "models/password_strength_model.pkl"
)