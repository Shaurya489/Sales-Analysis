
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Superstore Dashboard", layout="wide")
st.title("Superstore Sales Dashboard")

df = pd.read_csv("experiment10_raw_dataset - experiment10_raw_dataset.csv")

df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

st.sidebar.header("Filters")
region = st.sidebar.multiselect(
    "Region", df["Region"].dropna().unique(),
    default=df["Region"].dropna().unique()
)
category = st.sidebar.multiselect(
    "Category", df["Category"].dropna().unique(),
    default=df["Category"].dropna().unique()
)
segment = st.sidebar.multiselect(
    "Segment", df["Segment"].dropna().unique(),
    default=df["Segment"].dropna().unique()
)

filtered = df[
    df["Region"].isin(region) &
    df["Category"].isin(category) &
    df["Segment"].isin(segment)
]

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"{filtered['Sales'].sum():,.2f}")
col2.metric("Total Profit", f"{filtered['Profit'].sum():,.2f}")
col3.metric("Total Orders", filtered["Order ID"].nunique())

left, right = st.columns(2)

sales_data = filtered.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=False)

fig, ax = plt.subplots()
ax.bar(sales_data.index, sales_data.values)
ax.set_title("Sales by Sub-Category")
ax.set_xlabel("Sub-Category")
ax.set_ylabel("Sales")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
left.pyplot(fig)
plt.close(fig)

segment_data = filtered.groupby("Segment")["Sales"].sum()

fig, ax = plt.subplots()
ax.pie(segment_data.values, labels=segment_data.index, autopct="%1.1f%%")
ax.set_title("Sales by Segment")
right.pyplot(fig)
plt.close(fig)

st.subheader("Dataset Information")
st.write("Rows:", df.shape[0], "Columns:", df.shape[1])
st.write(df.dtypes.astype(str))

st.subheader("Filtered Data")
st.dataframe(filtered)
