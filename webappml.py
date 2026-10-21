
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Superstore Dashboard", layout="wide")
st.title("Superstore Sales Dashboard")


# Load your dataset directly
df = pd.read_csv("experiment10_raw_dataset - experiment10_raw_dataset(2).csv")


# Data cleaning
def clean_data(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].map(
            lambda x: x.strip() if isinstance(x, str) else x
        )
        df[col] = df[col].replace("", pd.NA)

    for col in ["Order Date", "Ship Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["Sales", "Profit", "Quantity", "Discount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = clean_data(df)


# 1. Data validation
st.header("1. Data Validation")

col1, col2, col3 = st.columns(3)
col1.metric("Rows", df.shape[0])
col2.metric("Columns", df.shape[1])
col3.metric("Duplicate Records", int(df.duplicated().sum()))

st.subheader("Column Names")
st.write(df.columns.tolist())

st.subheader("Data Types")
st.write(df.dtypes.astype(str))

st.subheader("Missing Values")
st.write(df.isnull().sum())

st.subheader("Statistical Summary")
st.dataframe(df.describe(include="all").T, use_container_width=True)


# 2. Data preprocessing
st.header("2. Data Preprocessing")

remove_duplicates = st.checkbox("Remove duplicate records", value=True)

missing_option = st.selectbox(
    "Handle missing values",
    ["Keep as is", "Remove rows with missing values", "Fill missing values"]
)

if remove_duplicates:
    df = df.drop_duplicates()

if missing_option == "Remove rows with missing values":
    df = df.dropna()

elif missing_option == "Fill missing values":
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            median = df[col].median()
            if pd.notna(median):
                df[col] = df[col].fillna(median)
        else:
            mode = df[col].mode()
            if not mode.empty:
                df[col] = df[col].fillna(mode[0])

st.write("Processed dimensions:", df.shape)

st.download_button(
    "Download Cleaned CSV",
    df.to_csv(index=False).encode("utf-8"),
    "cleaned_data.csv",
    "text/csv"
)


# 3. Interactive filters
st.sidebar.header("Filters")

filtered = df.copy()

for col in ["Region", "Category", "Segment"]:
    values = sorted(filtered[col].dropna().unique().tolist(), key=str)

    selected = st.sidebar.multiselect(
        col, values, default=values
    )

    filtered = filtered[filtered[col].isin(selected)]


# Date filter
dates = filtered["Order Date"].dropna()

if not dates.empty:
    date_range = st.sidebar.date_input(
        "Order Date Range",
        value=(dates.min().date(), dates.max().date())
    )

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start, end = date_range
        filtered = filtered[
            filtered["Order Date"].dt.date.between(start, end)
        ]


# 4. Five KPIs
st.header("3. Key Performance Indicators")

sales = filtered["Sales"].sum()
profit = filtered["Profit"].sum()
orders = filtered["Order ID"].nunique()
quantity = filtered["Quantity"].sum()

margin = profit / sales * 100 if sales != 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Sales", f"{sales:,.2f}")
col2.metric("Total Profit", f"{profit:,.2f}")
col3.metric("Total Orders", f"{orders:,}")
col4.metric("Quantity Sold", f"{quantity:,.0f}")
col5.metric("Profit Margin", f"{margin:.2f}%")


# 5. Visualizations
st.header("4. Sales Visualizations")

left, right = st.columns(2)


# Chart 1: Sales by Sub-Category
sales_data = filtered.groupby("Sub-Category")["Sales"].sum()
sales_data = sales_data.sort_values(ascending=False)

fig, ax = plt.subplots()
ax.bar(sales_data.index, sales_data.values)
ax.set_title("Sales by Sub-Category")
ax.set_xlabel("Sub-Category")
ax.set_ylabel("Sales")
ax.tick_params(axis="x", rotation=45)
fig.tight_layout()
left.pyplot(fig)
plt.close(fig)


# Chart 2: Sales by Segment
segment_data = filtered.groupby("Segment")["Sales"].sum()

fig, ax = plt.subplots()
if segment_data.sum() > 0:
    ax.pie(
        segment_data.values,
        labels=segment_data.index,
        autopct="%1.1f%%"
    )
    ax.set_title("Sales by Segment")
else:
    ax.text(0.5, 0.5, "No sales data", ha="center")
    ax.axis("off")

right.pyplot(fig)
plt.close(fig)


# Chart 3: Monthly Sales Trend
date_data = filtered.dropna(subset=["Order Date"]).copy()

if not date_data.empty:
    monthly_sales = (
        date_data.set_index("Order Date")["Sales"]
        .resample("MS")
        .sum()
    )

    fig, ax = plt.subplots()
    ax.plot(monthly_sales.index, monthly_sales.values, marker="o")
    ax.set_title("Monthly Sales Trend")
    ax.set_xlabel("Order Date")
    ax.set_ylabel("Sales")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# 6. Dataset information
st.header("5. Dataset Information")

st.write("Rows:", df.shape[0], "Columns:", df.shape[1])
st.write(df.dtypes.astype(str))

st.subheader("Filtered Data")
st.dataframe(filtered, use_container_width=True)
