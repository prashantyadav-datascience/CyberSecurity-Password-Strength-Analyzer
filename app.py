import re
import pickle

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(
    page_title="Cybersecurity Password Analyzer",
    page_icon="🔐",
    layout="wide"
)


# ==============================
# LOAD MODEL
# ==============================

@st.cache_resource
def load_model():

    with open(
        "models/password_strength_model.pkl",
        "rb"
    ) as file:

        return pickle.load(file)


package = load_model()

model = package["model"]
feature_names = package["features"]
model_accuracy = package["accuracy"]
classes = package["classes"]


# ==============================
# COMMON PASSWORDS
# ==============================

common_passwords = {
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
}


# ==============================
# FEATURE FUNCTIONS
# ==============================

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

    return int(
        any(
            seq in password
            for seq in sequences
        )
    )


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

    repeated_chars = repeated_character_count(
        password
    )

    common_password = int(
        password.lower() in common_passwords
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


# ==============================
# HEADER
# ==============================

st.title(
    "🔐 Cybersecurity Password Strength & Breach Risk Analyzer"
)

st.caption(
    "Machine Learning Powered Password Security Assessment"
)


# ==============================
# SIDEBAR
# ==============================

st.sidebar.title(
    "🛡️ Security Analyzer"
)

st.sidebar.info(
    "Password analysis is performed locally. "
    "The password is not sent to an external service."
)

st.sidebar.metric(
    "Model Accuracy",
    f"{model_accuracy * 100:.2f}%"
)

st.sidebar.markdown(
    """
### Machine Learning Model

**Random Forest Classifier**

Features used:

- Password Length
- Lowercase Characters
- Uppercase Characters
- Digits
- Special Characters
- Unique Characters
- Entropy
- Repeated Characters
- Common Password
- Sequential Pattern
- Digit Ratio
- Special Ratio
- Unique Ratio
"""
)


# ==============================
# PASSWORD INPUT
# ==============================

st.subheader("🔑 Enter Password")

password = st.text_input(
    "Password",
    type="password",
    placeholder="Enter password for analysis"
)


if password:

    # ==============================
    # PREDICTION
    # ==============================

    feature_values = extract_features(password)

    input_df = pd.DataFrame(
        [feature_values],
        columns=feature_names
    )

    prediction = model.predict(
        input_df
    )[0]

    probabilities = model.predict_proba(
        input_df
    )[0]

    strength = classes[prediction]

    confidence = max(probabilities) * 100


    # ==============================
    # RISK
    # ==============================

    if (
        password.lower() in common_passwords
        or len(password) < 8
    ):

        risk = "HIGH"

    elif strength == "Medium":

        risk = "MEDIUM"

    else:

        risk = "LOW"


    # ==============================
    # SCORE
    # ==============================

    if strength == "Weak":

        score = 30

    elif strength == "Medium":

        score = 65

    else:

        score = 95


    # ==============================
    # METRICS
    # ==============================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Password Length",
            len(password)
        )

    with col2:

        st.metric(
            "Entropy",
            f"{calculate_entropy(password):.1f} bits"
        )

    with col3:

        st.metric(
            "ML Confidence",
            f"{confidence:.1f}%"
        )

    with col4:

        st.metric(
            "Risk Level",
            risk
        )


    st.divider()


    # ==============================
    # GAUGE
    # ==============================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "🎯 Password Strength Score"
        )

        fig_gauge = go.Figure(

            go.Indicator(

                mode="gauge+number",

                value=score,

                title={
                    "text": strength
                },

                gauge={

                    "axis": {
                        "range": [0, 100]
                    },

                    "steps": [

                        {
                            "range": [0, 40],
                            "color": "#ff4b4b"
                        },

                        {
                            "range": [40, 70],
                            "color": "#ffa500"
                        },

                        {
                            "range": [70, 100],
                            "color": "#21c354"
                        }

                    ]

                }

            )

        )

        st.plotly_chart(
            fig_gauge,
            use_container_width=True
        )


    # ==============================
    # PROBABILITY CHART
    # ==============================

    with col2:

        st.subheader(
            "📊 Prediction Probability"
        )

        probability_df = pd.DataFrame({

            "Strength": classes,

            "Probability": probabilities * 100

        })

        fig_probability = go.Figure(

            go.Bar(

                x=probability_df["Strength"],

                y=probability_df["Probability"],

                text=[
                    f"{x:.1f}%"
                    for x in probability_df["Probability"]
                ],

                textposition="auto"

            )

        )

        fig_probability.update_layout(

            yaxis_title="Probability (%)",

            xaxis_title="Password Strength",

            yaxis={
                "range": [0, 100]
            }

        )

        st.plotly_chart(
            fig_probability,
            use_container_width=True
        )


    # ==============================
    # SECURITY ASSESSMENT
    # ==============================

    st.subheader(
        "🛡️ Security Assessment"
    )

    if risk == "HIGH":

        st.error(
            "🚨 HIGH RISK — This password should not be used."
        )

    elif risk == "MEDIUM":

        st.warning(
            "⚠️ MEDIUM RISK — Improve password complexity."
        )

    else:

        st.success(
            "✅ LOW RISK — Password has strong complexity characteristics."
        )


    # ==============================
    # FEATURES
    # ==============================

    st.subheader(
        "🔍 Password Features"
    )

    feature_display = pd.DataFrame({

        "Feature": [

            "Length",
            "Lowercase Characters",
            "Uppercase Characters",
            "Digits",
            "Special Characters",
            "Unique Characters",
            "Entropy",
            "Repeated Characters",
            "Common Password",
            "Sequential Pattern"

        ],

        "Value": [

            len(password),

            sum(
                c.islower()
                for c in password
            ),

            sum(
                c.isupper()
                for c in password
            ),

            sum(
                c.isdigit()
                for c in password
            ),

            sum(
                not c.isalnum()
                for c in password
            ),

            len(set(password)),

            f"{calculate_entropy(password):.2f} bits",

            repeated_character_count(
                password
            ),

            "Yes"
            if password.lower()
            in common_passwords
            else "No",

            "Yes"
            if has_sequence(password)
            else "No"

        ]

    })

    st.dataframe(
        feature_display,
        use_container_width=True,
        hide_index=True
    )


    # ==============================
    # RECOMMENDATIONS
    # ==============================

    st.subheader(
        "💡 Security Recommendations"
    )

    recommendations = []


    if len(password) < 12:

        recommendations.append(
            "Use at least 12 characters."
        )


    if not re.search(
        r"[A-Z]",
        password
    ):

        recommendations.append(
            "Add uppercase letters."
        )


    if not re.search(
        r"[a-z]",
        password
    ):

        recommendations.append(
            "Add lowercase letters."
        )


    if not re.search(
        r"[0-9]",
        password
    ):

        recommendations.append(
            "Add numbers."
        )


    if not re.search(
        r"[^a-zA-Z0-9]",
        password
    ):

        recommendations.append(
            "Add special characters."
        )


    if password.lower() in common_passwords:

        recommendations.append(
            "Avoid commonly used passwords."
        )


    if has_sequence(password):

        recommendations.append(
            "Avoid predictable sequences."
        )


    if not recommendations:

        recommendations.append(
            "Password follows strong complexity patterns."
        )


    for recommendation in recommendations:

        st.write(
            "✔️ " + recommendation
        )