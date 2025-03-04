import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime

# Load data
# ID file Google Drive
file_id = "1_xWcrk4vjpTHWm1QzoxZhb9clLyM3b-5"
url = f"https://drive.google.com/uc?id={file_id}"

# Baca dataset
merged_df = pd.read_csv(url)
# Data Preparation
merged_df['order_purchase_timestamp'] = pd.to_datetime(merged_df['order_purchase_timestamp'])
merged_df['year_month'] = merged_df['order_purchase_timestamp'].dt.to_period('M')

# Streamlit App configuration
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# Header
st.markdown("<h1 style='text-align: center;'>Sales Dashboard</h1>", unsafe_allow_html=True)  # Menggunakan HTML untuk memperbesar

# Sidebar Filters
st.sidebar.header("Filters")

# Dropdown for Order Status with "Semua" option
order_status_options = ["All order Status"] + merged_df['order_status'].unique().tolist()
order_status_filter = st.sidebar.selectbox("Select Order Status", options=order_status_options)

# Dropdown for Payment Type with "Semua" option
payment_type_options = ["All Payment"] + merged_df['payment_type'].unique().tolist()
payment_type_filter = st.sidebar.selectbox("Select Payment Type", options=payment_type_options)

# Dropdown for Seller City with "All Cities" option
seller_cities = ['All Cities'] + sorted(merged_df['seller_city'].unique().tolist())  
seller_city_filter = st.sidebar.selectbox("Select Seller City", options=seller_cities)

# Date range filter
date_range = st.sidebar.date_input("Select Date Range", 
                                   [merged_df['order_purchase_timestamp'].min().date(), 
                                    merged_df['order_purchase_timestamp'].max().date()])

# Apply filters
filtered_df = merged_df[
    ((merged_df['order_status'] == order_status_filter) | (order_status_filter == "All order Status")) &
    ((merged_df['payment_type'] == payment_type_filter) | (payment_type_filter == "All Payment")) &
    ((merged_df['seller_city'] == seller_city_filter) if seller_city_filter != 'All Cities' else True) & 
    (merged_df['order_purchase_timestamp'].dt.date >= date_range[0]) & 
    (merged_df['order_purchase_timestamp'].dt.date <= date_range[1])
]

# Display filtered data count
st.sidebar.write(f"**Total Filtered Orders: {len(filtered_df):,}**")

# Scorecard

# Calculate metrics
total_orders = filtered_df['order_id'].nunique()
total_revenue = filtered_df['payment_value'].sum()
total_customers = filtered_df['customer_id'].nunique()
total_sellers = filtered_df['seller_id'].nunique()
average_order_value = total_revenue / total_orders if total_orders > 0 else 0

# Display metrics in boxes with borders and labels
scorecard_html = f"""
<div style="display: flex; justify-content: space-around; margin-bottom: 20px;">
    <div style="border: 1px solid #B0CDE0; border-radius: 5px; padding: 10px; width: 150px; text-align: center;">
        <h5 style="margin: 0;">Total Orders</h5>
        <p style="margin: 0;">{total_orders}</p>
    </div>
    <div style="border: 1px solid #B0CDE0; border-radius: 5px; padding: 10px; width: 150px; text-align: center;">
        <h5 style="margin: 0;">Total Revenue</h5>
        <p style="margin: 0;">${total_revenue:,.2f}</p>
    </div>
    <div style="border: 1px solid #B0CDE0; border-radius: 5px; padding: 10px; width: 150px; text-align: center;">
        <h5 style="margin: 0;">Total Customers</h5>
        <p style="margin: 0;">{total_customers}</p>
    </div>
    <div style="border: 1px solid #B0CDE0; border-radius: 5px; padding: 10px; width: 150px; text-align: center;">
        <h5 style="margin: 0;">Total Sellers</h5>
        <p style="margin: 0;">{total_sellers}</p>
    </div>
    <div style="border: 1px solid #B0CDE0; border-radius: 5px; padding: 10px; width: 150px; text-align: center;">
        <h5 style="margin: 0;">Average Order Value (AOV)</h5>
        <p style="margin: 0;">${average_order_value:,.2f}</p>
    </div>
</div>
"""

st.markdown(scorecard_html, unsafe_allow_html=True)

# Dashboard Layout
with st.container():
    col1, col2 = st.columns(2)

    # Bar Chart for Payment Types
    with col1:
        st.subheader("Distribution of Payment Types")  # Menggunakan subheader
        payment_type = filtered_df['payment_type'].value_counts().reset_index()
        payment_type.columns = ['payment_type', 'total_sales']

        # Membuat horizontal bar chart dengan ukuran yang lebih kecil
        fig, ax = plt.subplots(figsize=(5, 3))  # Ukuran figure yang lebih kecil
        sns.barplot(y='payment_type', x='total_sales', data=payment_type, color='#B0CDE0', ax=ax)
        ax.set_title("Bar Chart of Payment Types")
        ax.set_xlabel("Total Sales")
        ax.set_ylabel("Payment Type")

        # Add text labels on bars
        for p in ax.patches:
            ax.annotate(f"{p.get_width():,.0f}", 
                        (p.get_width(), p.get_y() + p.get_height() / 2),
                        xytext=(5, 0), textcoords="offset points", 
                        ha='left', va='center', fontsize=10, color='black')

        st.pyplot(fig)

    # Monthly Orders Trend (Line Chart)
    with col2:
        st.subheader("Monthly Orders Trend")  # Menggunakan subheader
        monthly_orders = filtered_df.groupby('year_month')['order_id'].count().reset_index()
        monthly_orders['year_month'] = monthly_orders['year_month'].astype(str)

        fig2, ax2 = plt.subplots(figsize=(8, 4))  # Ukuran figure konsisten
        ax2.plot(monthly_orders['year_month'], monthly_orders['order_id'], marker='o', linestyle='-', color='b')

        # Add text labels on points
        for i, txt in enumerate(monthly_orders['order_id']):
            ax2.annotate(f"{txt}", (monthly_orders['year_month'][i], monthly_orders['order_id'][i]),
                        textcoords="offset points", xytext=(0, 5), ha='center', fontsize=10, color='black')

        ax2.set_xticklabels(monthly_orders['year_month'], rotation=45)
        ax2.set_xlabel("Month-Year")
        ax2.set_ylabel("Number of Orders")
        ax2.set_title("Monthly Orders Trend")
        ax2.grid(True)

        st.pyplot(fig2)

# RFM Analysis
st.subheader("RFM Analysis")  # Menggunakan subheader
current_date = datetime.now()

recency_df = filtered_df.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (current_date - x.max()).days
}).reset_index()
recency_df.rename(columns={'order_purchase_timestamp': 'Recency'}, inplace=True)

frequency_df = filtered_df.groupby('customer_id').agg({
    'order_id': 'count'
}).reset_index()
frequency_df.rename(columns={'order_id': 'Frequency'}, inplace=True)

monetary_df = filtered_df.groupby('customer_id').agg({
    'payment_value': 'sum'
}).reset_index()
monetary_df.rename(columns={'payment_value': 'Monetary'}, inplace=True)

rfm_df = recency_df.merge(frequency_df, on='customer_id')
rfm_df = rfm_df.merge(monetary_df, on='customer_id')

# RFM Visualization (Separated but side by side)
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Top 5 Customers by Recency")  # Menggunakan subheader
    top_recency = rfm_df.nsmallest(5, 'Recency')
    fig, ax = plt.subplots(figsize=(8, 4))  # Ukuran figure konsisten
    sns.barplot(y="Recency", x="customer_id", data=top_recency, color="#B0CDE0", ax=ax)
    ax.set_xticklabels(top_recency['customer_id'], rotation=90)
    ax.set_ylim(0, top_recency['Recency'].max() * 1.1)  # Add margin

    for p in ax.patches:
        ax.annotate(f"{p.get_height():,.0f}", 
                    (p.get_x() + p.get_width() / 2, p.get_height()),
                    xytext=(0, -10), textcoords=" offset points", ha="center", fontsize=10, color='black')

    st.pyplot(fig)

with col2:
    st.subheader("Top 5 Customers by Frequency")  # Menggunakan subheader
    top_frequency = rfm_df.nlargest(5, 'Frequency')
    fig, ax = plt.subplots(figsize=(8, 4))  # Ukuran figure konsisten
    sns.barplot(y="Frequency", x="customer_id", data=top_frequency, color="#B0CDE0", ax=ax)
    ax.set_xticklabels(top_frequency['customer_id'], rotation=90)
    ax.set_ylim(0, top_frequency['Frequency'].max() * 1.1)  # Add margin

    for p in ax.patches:
        ax.annotate(f"{p.get_height():,.0f}", 
                    (p.get_x() + p.get_width() / 2, p.get_height()),
                    xytext=(0, -10), textcoords="offset points", ha="center", fontsize=10, color='black')

    st.pyplot(fig)

with col3:
    st.subheader("Top 5 Customers by Monetary")  # Menggunakan subheader
    top_monetary = rfm_df.nlargest(5, 'Monetary')
    fig, ax = plt.subplots(figsize=(8, 4))  # Ukuran figure konsisten
    sns.barplot(y="Monetary", x="customer_id", data=top_monetary, color="#B0CDE0", ax=ax)
    ax.set_xticklabels(top_monetary['customer_id'], rotation=90)
    ax.set_ylim(0, top_monetary['Monetary'].max() * 1.1)  # Add margin

    for p in ax.patches:
        ax.annotate(f"{p.get_height():,.0f}", 
                    (p.get_x() + p.get_width() / 2, p.get_height()),
                    xytext=(0, -10), textcoords="offset points", ha="center", fontsize=10, color='black')

    st.pyplot(fig)

# Additional Visualizations
st.subheader("Top Cities and Best-Selling Categories")  # Menggunakan subheader
col1, col2 = st.columns(2)

# Top 10 Cities with Highest Sales
with col1:
    city_sales = merged_df.groupby('seller_city')['order_id'].nunique().reset_index()
    city_sales = city_sales.sort_values(by='order_id', ascending=False)
    fig3, ax3 = plt.subplots(figsize=(8, 4))  # Ukuran figure konsisten
    sns.barplot(x=city_sales.head(10)['order_id'], y=city_sales.head(10)['seller_city'], color="#B0CDE0", ax=ax3)
    ax3.set_xlabel("Jumlah Pesanan")
    ax3.set_ylabel("Kota Penjual")
    ax3.set_title("Top 10 Kota dengan Penjualan Tertinggi")

    for index, value in enumerate(city_sales.head(10)['order_id']):
        ax3.text(value + 1, index, str(value), va='center', fontsize=10, color='black')

    st.pyplot(fig3)

# Best-Selling Product Categories in the Top City
with col2:
    top_city = city_sales.iloc[0]['seller_city']
    top_city_products = merged_df[merged_df['seller_city'] == top_city]['product_category_name'].value_counts().head(10)
    fig4, ax4 = plt.subplots(figsize=(8, 4))  # Ukuran figure konsisten
    sns.barplot(x=top_city_products.values, y=top_city_products.index, color="#B0CDE0", ax=ax4)
    ax4.set_xlabel("Jumlah Produk Terjual")
    ax4.set_ylabel("Kategori Produk")
    ax4.set_title(f"Kategori Produk Paling Laku di {top_city}")

    for index, value in enumerate(top_city_products.values):
        ax4.text(value + 1, index, str(value), va='center', fontsize=10, color='black')

    st.pyplot(fig4)

# Run the app
if __name__ == "__main__":
    st.write("Streamlit app is running")
