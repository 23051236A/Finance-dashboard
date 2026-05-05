# 💰 Personal Finance Dashboard

An interactive web application built using Streamlit to analyze and manage personal expenses with smart insights and adaptive classification.

## 🚀 Features

* Upload CSV-based expense data
* Add new expenses with date & time
* Category-wise spending analysis
* Monthly trend visualization
* AI-based anomaly detection
* Adaptive Needs vs Wants classification (self-learning)
* Optional income-based budgeting system
* Smart financial insights and suggestions

## 🧠 Intelligent System

* Uses keyword + feedback-based classification
* Learns from user corrections and updates future predictions
* Detects unusual spending using Isolation Forest

## 📊 Tech Stack

* Python
* Pandas
* Streamlit
* Matplotlib
* Scikit-learn

## ▶️ Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Data Format

CSV should contain:

* Date (with time)
* Amount
* Category
* Description

## 🎯 Use Case

Helps users track spending, classify expenses intelligently, and make better financial decisions.

## 🔮 Future Improvements

* ML-based classification model
* Category-wise budget limits
* Interactive charts (Plotly)
* Cloud deployment with user accounts
