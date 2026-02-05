# Enhanced UAE Retail Insights Streamlit App
# Focus: More filters, better UX, colourful visuals, business-friendly insights

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="UAE Retail Insights Dashboard",
    page_icon="📊",
    layout="wide",
)

# ---------------- CUSTOM CSS ----------------
st.markdown(
    """
    <style>
    .main {
        background-color: #f6f8fb;
    }
    h1, h2, h3 {
        color: #1f2c56;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    # Replace with your cleaned dataset path
    df = pd.read_csv("retail_cleaned.csv")
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Month Name'] = df['Order Date'].dt.month_name()
    return df

try:
    df = load_data()
except:
    st.error("Please upload 'retail_cleaned.csv' in the same folder.")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("🔎 Advanced Filters")

# Date Filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['Order Date'].min(), df['Order Date'].max()]
)

# Multi-select filters
category_filter = st.sidebar.multiselect(
    "Category",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

sub_category_filter = st.sidebar.multiselect(
    "Sub-Category",
    options=df['Sub-Category'].unique(),
    default=df['Sub-Category'].unique()
)

region_filter = st.sidebar.multiselect(
    "Region",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

segment_filter = st.sidebar.multiselect(
    "Customer Segment",
    options=df['Segment'].unique(),
    default=df['Segment'].unique()
)

profit_range = st.sidebar.slider(
    "Profit Range",
    float(df['Profit'].min()),
    float(df['Profit'].max()),
    (float(df['Profit'].min()), float(df['Profit'].max()))
)

# ---------------- APPLY FILTERS ----------------
filtered_df = df[
    (df['Order Date'] >= pd.to_datetime(date_range[0])) &
    (df['Order Date'] <= pd.to_datetime(date_range[1])) &
    (df['Category'].isin(category_filter)) &
    (df['Sub-Category'].isin(sub_category_filter)) &
    (df['Region'].isin(region_filter)) &
    (df['Segment'].isin(segment_filter)) &
    (df['Profit'] >= profit_range[0]) &
    (df['Profit'] <= profit_range[1])
]

# ---------------- HEADER ----------------
st.title("📊 UAE Retail Insights Dashboard")
st.caption("Interactive business intelligence dashboard for retail performance analysis")

# ---------------- KPI SECTION ----------------
k1, k2, k3, k4 = st.columns(4)

k1.metric("💰 Total Revenue", f"{filtered_df['Sales'].sum():,.0f}")
k2.metric("📈 Total Profit", f"{filtered_df['Profit'].sum():,.0f}")
k3.metric("🧾 Total Orders", filtered_df['Order ID'].nunique())
k4.metric("👥 Customers", filtered_df['Customer ID'].nunique())

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Sales Analysis",
    "📊 Category Performance",
    "🌍 Regional Insights",
    "🔮 Advanced Insights"
])

# ---------------- TAB 1: SALES ----------------
with tab1:
    st.subheader("Sales Trend Over Time")
    sales_trend = filtered_df.groupby('Order Date')['Sales'].sum().reset_index()
    fig = px.line(
        sales_trend,
        x='Order Date',
        y='Sales',
        markers=True,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Revenue Heatmap")
    heatmap_df = filtered_df.groupby(['Year', 'Month Name'])['Sales'].sum().reset_index()
    heatmap_pivot = heatmap_df.pivot(index='Year', columns='Month Name', values='Sales')
    fig2 = px.imshow(
        heatmap_pivot,
        color_continuous_scale='Blues',
        aspect='auto'
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- TAB 2: CATEGORY ----------------
with tab2:
    st.subheader("Category-wise Revenue & Profit")
    cat_df = filtered_df.groupby('Category')[['Sales', 'Profit']].sum().reset_index()
    fig = px.bar(
        cat_df,
        x='Category',
        y=['Sales', 'Profit'],
        barmode='group',
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Sub-Categories by Profit")
    sub_df = filtered_df.groupby('Sub-Category')['Profit'].sum().sort_values(ascending=False).head(10).reset_index()
    fig2 = px.bar(
        sub_df,
        x='Profit',
        y='Sub-Category',
        orientation='h',
        color='Profit',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- TAB 3: REGION ----------------
with tab3:
    st.subheader("Region-wise Sales Distribution")
    reg_df = filtered_df.groupby('Region')['Sales'].sum().reset_index()
    fig = px.pie(
        reg_df,
        names='Region',
        values='Sales',
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Profit vs Discount Analysis")
    fig2 = px.scatter(
        filtered_df,
        x='Discount',
        y='Profit',
        color='Category',
        size='Sales',
        template='plotly_white'
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- TAB 4: ADVANCED ----------------
with tab4:
    st.subheader("Loss-Making Orders")
    loss_df = filtered_df[filtered_df['Profit'] < 0]
    st.dataframe(loss_df[['Order ID', 'Category', 'Sales', 'Profit', 'Discount']])

    st.subheader("Key Business Takeaways")
    st.markdown(
        """
        - 📌 Focus on high-profit sub-categories with low discount dependency
        - 📌 Certain regions show high revenue but low margins
        - 📌 Excessive discounting correlates with losses
        - 📌 Opportunity to optimise pricing strategies
        """
    )

# ---------------- DOWNLOAD ----------------
st.download_button(
    "⬇️ Download Filtered Data",
    filtered_df.to_csv(index=False),
    file_name="filtered_retail_data.csv",
    mime="text/csv"
)
