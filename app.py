import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import os

st.set_page_config(page_title="FINANCE DASHBOARD", layout="wide")

st.markdown("""
<h1 style='text-align: center; color: white; font-size: 42px; margin-bottom: 5px;'>
💰 Personal Finance Dashboard
</h1>
<p style='text-align: center; color: #9aa0a6; font-size: 14px;'>
Track • Analyze • Improve your spending habits
</p>
<hr style='border: 1px solid rgba(255,255,255,0.1); margin-bottom: 25px;'>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.stApp { background-color: #0E1117; }
.block-container { padding-top: 2rem; }
[data-testid="metric-container"] {
    background-color: #111827;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #1f2937;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
}
section[data-testid="stSidebar"] { background-color: #111827; }
.stDownloadButton button {
    background-color: #00C9A7;
    color: black;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

use_budget = st.toggle("Enable Budget Planning")

salary = 0
savings_goal = 20

if use_budget:
    colA, colB = st.columns(2)
    with colA:
        salary = st.number_input("💰 Monthly Salary", min_value=0)
    with colB:
        savings_goal = st.slider("🎯 Savings Goal (%)", 10, 50, 20)

file = st.file_uploader("Upload your expenses CSV")

if os.path.exists("category_map.csv"):
    category_map = pd.read_csv("category_map.csv")
else:
    category_map = pd.DataFrame(columns=["Category", "Type"])

needs_keywords = ["rent", "food", "grocery", "transport", "electricity", "bill"]
wants_keywords = ["shopping", "movie", "entertainment", "travel", "clothes", "luxury"]

def classify_category(category):
    category_lower = str(category).lower()
    match = category_map[category_map["Category"].str.lower() == category_lower]
    if not match.empty:
        return match["Type"].values[0]
    for word in needs_keywords:
        if word in category_lower:
            return "Needs"
    for word in wants_keywords:
        if word in category_lower:
            return "Wants"
    return "Other"

if file:
    df = pd.read_csv(file)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Type"] = df["Category"].apply(classify_category)

    st.markdown("## ➕ Add New Expense")

    with st.expander("Click to add expense"):
        date_input = st.date_input("Date")
        time_input = st.time_input("Time")
        new_date = pd.to_datetime(f"{date_input} {time_input}")

        new_amount = st.number_input("Amount", min_value=0)
        new_category = st.text_input("Category")
        new_desc = st.text_input("Description")

        if st.button("Add Expense"):
            new_row = pd.DataFrame({
                "Date": [new_date],
                "Amount": [new_amount],
                "Category": [new_category],
                "Description": [new_desc]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv("expenses.csv", index=False)
            st.success("Expense added successfully! Refresh to see changes.")

    st.subheader("DATA PREVIEW")
    st.dataframe(df)

    st.download_button(
        label="Download Data",
        data=df.to_csv(index=False),
        file_name="expenses.csv",
        mime="text/csv"
    )

    st.markdown("### 🧠 Improve Classification")

    unique_categories = df["Category"].unique()

    for cat in unique_categories:
        current_type = classify_category(cat)

        new_type = st.selectbox(
            f"{cat}",
            ["Needs", "Wants", "Other"],
            index=["Needs", "Wants", "Other"].index(current_type),
            key=cat
        )

        if new_type != current_type:
            new_entry = pd.DataFrame({
                "Category": [cat],
                "Type": [new_type]
            })

            category_map = pd.concat([category_map, new_entry], ignore_index=True)
            category_map.drop_duplicates(subset="Category", keep="last", inplace=True)
            category_map.to_csv("category_map.csv", index=False)

            st.success(f"Updated: {cat} → {new_type}")

    st.markdown("---")

    st.sidebar.header("FILTER")
    selected_category = st.sidebar.selectbox(
        "Select Category",
        ["All"] + list(df["Category"].unique())
    )

    if selected_category != "All":
        df = df[df["Category"] == selected_category]

    category_spending = df.groupby("Category")["Amount"].sum()

    model = IsolationForest(contamination=0.1, random_state=42)
    df["Anomaly"] = model.fit_predict(df[["Amount"]])
    threshold = df["Amount"].quantile(0.95)

    anomalies = df[
        (df["Anomaly"] == -1) &
        (df["Amount"] > threshold)
    ]

    top_category = category_spending.idxmax()
    total_spend = df["Amount"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("💸 Total Spending", f"₹{total_spend}")
    col2.metric("🏆 Top Category", top_category)
    col3.metric("📊 Categories", df["Category"].nunique())

    if use_budget and salary > 0:
        needs_budget = salary * 0.5
        wants_budget = salary * 0.3
        savings_target = salary * (savings_goal / 100)

        needs_spend = df[df["Type"] == "Needs"]["Amount"].sum()
        wants_spend = df[df["Type"] == "Wants"]["Amount"].sum()

        st.markdown("### 💼 Budget Overview")
        b1, b2, b3 = st.columns(3)
        b1.metric("🏠 Needs", f"₹{int(needs_spend)} / ₹{int(needs_budget)}")
        b2.metric("🛍 Wants", f"₹{int(wants_spend)} / ₹{int(wants_budget)}")
        b3.metric("💰 Savings Target", f"₹{int(savings_target)}")

    colA, colB = st.columns(2)

    with colA:
        st.markdown("### 📊 Spending by Category")
        st.bar_chart(category_spending, use_container_width=True)

    with colB:
        st.markdown("### 📈 Monthly Spending Trend")
        monthly_spending = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()
        st.line_chart(monthly_spending)

    st.markdown("---")

    st.markdown("### 🍩 Spending Distribution")

    fig, ax = plt.subplots()
    ax.set_facecolor('#0E1117')
    fig.patch.set_facecolor('#0E1117')

    wedges, texts, autotexts = ax.pie(
        category_spending,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.6,
        textprops={'color': 'white', 'fontsize': 11, 'weight': 'bold'},
        wedgeprops={'edgecolor': '#0E1117', 'linewidth': 2}
    )

    for text in texts:
        text.set_visible(False)

    ax.legend(
        wedges,
        category_spending.index,
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        frameon=False,
        labelcolor='white'
    )

    ax.set_ylabel("")
    st.pyplot(fig)

    st.markdown("---")

    st.markdown("### 🚨 Unusual Expenses")

    if not anomalies.empty:
        st.dataframe(anomalies)
    else:
        st.success("No unusual spending detected")

    st.markdown("---")

    st.markdown("### 🧠 Insights")

    percentage = (category_spending / category_spending.sum()) * 100

    if percentage[top_category] > 40:
        st.error(f"High spending on {top_category} ({percentage[top_category]:.1f}%)")
    elif percentage[top_category] > 25:
        st.warning(f"Moderate spending on {top_category}")
    else:
        st.success("Spending is balanced")

    df["Month"] = df["Date"].dt.to_period("M")
    monthly = df.groupby("Month")["Amount"].sum()

    if len(monthly) > 1:
        change = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2]) * 100
        st.info(f"Spending change from last month: {change:.2f}%")

    st.markdown("### 💡 Smart Suggestions")

    if percentage[top_category] > 40:
        st.warning(f"Reduce spending on {top_category}")
    elif percentage[top_category] > 25:
        st.info(f"Monitor {top_category} spending")
    else:
        st.success("Healthy spending pattern")

    monthly_avg = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum().mean()
    st.info(f"Suggested monthly budget (history-based): ₹{int(monthly_avg)}")

    if use_budget and salary > 0:
        st.markdown("### 🏦 Savings Analysis")

        actual_savings = salary - total_spend

        if actual_savings >= savings_target:
            st.success(f"You saved ₹{int(actual_savings)}")
        else:
            st.warning(f"Below savings goal. Saved: ₹{int(actual_savings)}")