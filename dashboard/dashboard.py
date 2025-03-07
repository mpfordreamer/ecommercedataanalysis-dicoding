import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title='E-Commerce Analysis Dashboard',
    layout='wide',
    page_icon='🛒'
)

# Load the data
@st.cache_data
def load_data():
    data = pd.read_csv('main_data.csv')
    # Convert datetime columns
    datetime_columns = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date',
        'shipping_limit_date',
        'review_creation_date',
        'review_answer_timestamp'
    ]
    for column in datetime_columns:
        data[column] = pd.to_datetime(data[column])
    return data

# Load data
df = load_data()

# Sidebar
st.sidebar.header('🛍️ E-Commerce Analysis Dashboard')

# Add dashboard description with better formatting
st.sidebar.markdown("""
### About This Dashboard
This is a Brazilian e-commerce analysis dashboard based on orders made at Olist Store.

#### Features:
- Order status and trends
- Price and payment analysis
- Freight performance
- Product characteristics
- Customer reviews

#### Data Source:
Brazilian E-Commerce Public Dataset by Olist
""")

st.sidebar.markdown('---')

st.sidebar.markdown('<div style="text-align: center;">Created by: I Dewa Gede Mahesta Parawangsa</div>', unsafe_allow_html=True)


# Main content
st.title('🛒 E-Commerce Analysis Dashboard')

# Create tabs for different analyses
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "About",
    "Order Trends & Characteristics", 
    "Top Product Categories",
    "Delivery Analysis",
    "Customer Reviews",
])
with tab1:
    # Create two columns
    col1, col2 = st.columns([2, 3])
    
    with col1:
        # Add Olist logo/image
        st.image('about.png', width=500)
    
    with col2:
        st.markdown(""" 
        ## About This Dashboard
        
        This dashboard provides comprehensive analysis of Brazilian E-commerce data from Olist Store. 
        Olist is the largest department store in Brazilian marketplaces. This dashboard helps 
        stakeholders understand business performance through various metrics and visualizations.
        
        ### 🏢 Company Overview
        Olist connects small businesses from all over Brazil to channels without hassle and 
        with a single contract. These merchants are able to sell their products through the 
        Olist Store and ship them directly to the customers using Olist logistics partners.
        """)
    
    st.markdown("---")
    
    # Create three columns for key metrics
    metric1, metric2, metric3, metric4 = st.columns(4)
    
    with metric1:
        st.metric(label="Total Orders", 
                 value=f"{len(df['order_id'].unique()):,}")
    
    with metric2:
        st.metric(label="Total Products", 
                 value=f"{len(df['product_id'].unique()):,}")
    
    with metric3:
        st.metric(label="Total Customers", 
                 value=f"{len(df['customer_id'].unique()):,}")
    
    with metric4:
        st.metric(label="Total Sellers", 
                 value=f"{len(df['seller_id'].unique()):,}")
    
    st.markdown("---")
    
    st.markdown("""
    ### 📊 Dataset Information
    
    #### Time Period
    - Orders placed from September 2016 to October 2018
    - Real commercial data from multiple marketplaces in Brazil
    
    #### Key Features Analyzed
    - **Order Processing**: Track order status from purchase to delivery
    - **Payment Analysis**: Various payment methods and installment options
    - **Product Categories**: Distribution and performance across categories
    - **Delivery Performance**: Delivery times and efficiency analysis
    - **Customer Satisfaction**: Review scores and feedback analysis
    
    #### Data Privacy
    All customer and seller information in this dataset is anonymized, and 
    order values have been properly normalized.
    """)

with tab2:
    st.header("Order Trends & Characteristics Analysis")
    
    # Monthly order trends
    monthly_orders = df.groupby(pd.Grouper(key='order_purchase_timestamp', freq='M')).size().reset_index()
    monthly_orders.columns = ['date', 'order_count']
    
    fig = px.line(monthly_orders, x='date', y='order_count',
                  title='Monthly Order Trends')
    st.plotly_chart(fig, use_container_width=True)
    
    # Daily order distribution
    df['day_of_week'] = df['order_purchase_timestamp'].dt.day_name()
    daily_orders = df['day_of_week'].value_counts()
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_orders = daily_orders.reindex(days_order)
    
    fig = px.bar(x=daily_orders.index, y=daily_orders.values,
                 title='Order Distribution by Day of Week')
    st.plotly_chart(fig, use_container_width=True)

    # Add quarter column
    df['quarter'] = df['order_purchase_timestamp'].dt.quarter
    df['year'] = df['order_purchase_timestamp'].dt.year

    # Calculate quarterly orders
    quarterly_orders = df.groupby(['year', 'quarter']).size().reset_index()
    quarterly_orders.columns = ['year', 'quarter', 'order_count']

    # Create quarter labels
    quarterly_orders['quarter_label'] = 'Q' + quarterly_orders['quarter'].astype(str) + ' ' + quarterly_orders['year'].astype(str)

    # Visualization
    fig = px.bar(quarterly_orders, x='quarter_label', y='order_count',
                 title='Quarterly Order Distribution')
    st.plotly_chart(fig, use_container_width=True)

    # Add month and year columns
    df['month'] = df['order_purchase_timestamp'].dt.month

    # Calculate monthly orders by year
    monthly_year_orders = df.groupby(['year', 'month']).size().reset_index()
    monthly_year_orders.columns = ['year', 'month', 'order_count']

    # Create month names and ensure correct order
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Create complete date range for all months in each year
    years = monthly_year_orders['year'].unique()
    complete_data = []
    for year in years:
        for month_num, month_name in enumerate(months, 1):
            order_count = monthly_year_orders[
                (monthly_year_orders['year'] == year) & 
                (monthly_year_orders['month'] == month_num)
            ]['order_count'].values
            complete_data.append({
                'year': year,
                'month': month_num,
                'month_name': month_name,
                'order_count': order_count[0] if len(order_count) > 0 else 0
            })

    # Convert to DataFrame and sort
    monthly_year_orders = pd.DataFrame(complete_data).sort_values(['year', 'month'])

    # Create a figure with larger size
    fig = px.line(monthly_year_orders, x='month_name', y='order_count', color='year',
                  title='Monthly Orders: Year-over-Year Comparison')
    st.plotly_chart(fig, use_container_width=True)

    # Order value distribution
    df['total_value'] = df['price'] + df['freight_value']
    
    fig = px.histogram(df[df['total_value'] <= 1000], x='total_value', nbins=50,
                      title='Distribution of Order Values (up to R$ 1000)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Payment type distribution
    payment_dist = df['payment_type'].value_counts()
    
    fig = px.pie(values=payment_dist.values, names=payment_dist.index,
                 title='Distribution of Payment Methods')
    st.plotly_chart(fig, use_container_width=True)

    # Customer Behavior Analysis
    st.header("Customer Behavior Analysis")

    # Calculate total value per order
    df['total_value'] = df['price'] + df['freight_value']

    # Get the latest date in the dataset to calculate recency
    max_date = df['order_purchase_timestamp'].max()

    # Group by customer_id to calculate metrics
    customer_metrics = df.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (max_date - x.max()).days,  # Days since last purchase
        'order_id': 'count',  # Number of purchases
        'total_value': 'sum'  # Total spending
    }).reset_index()

    # Rename columns
    customer_metrics.columns = ['customer_id', 'days_since_last_purchase', 'number_of_purchases', 'total_spending']

    # Create segments based on behaviors with 5 categories
    def customer_segment(row):
        days = row['days_since_last_purchase']
        purchases = row['number_of_purchases']
        spending = row['total_spending']
        
        if days <= 30 and purchases >= 5 and spending > 500:
            return 'VIP Customers'
        elif days <= 60 and purchases >= 3:
            return 'Loyal Customers'
        elif days <= 90 and purchases == 1:
            return 'New Customers'
        elif days > 90 and days <= 180:
            return 'At Risk'
        else:
            return 'Inactive Customers'

    customer_metrics['segment'] = customer_metrics.apply(customer_segment, axis=1)

    # Visualize customer segment distribution
    segment_counts = customer_metrics['segment'].value_counts().reset_index()
    segment_counts.columns = ['segment', 'count']

    fig = px.bar(segment_counts, y='segment', x='count', 
                title='Customer Segments Based on Behavior',
                color='segment',
                color_discrete_sequence=px.colors.qualitative.Set3,
                orientation='h')
    st.plotly_chart(fig, use_container_width=True)

    # Additional Visualization: Pie Chart to show segment proportions
    fig_pie = px.pie(segment_counts, values='count', names='segment',
                    title='Proportion of Customer Segments',
                    color='segment',
                    color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig_pie, use_container_width=True)

    # Display key metrics for each segment
    st.subheader("Key Metrics by Customer Segment")
    segment_stats = customer_metrics.groupby('segment').agg({
        'customer_id': 'count',
        'days_since_last_purchase': 'mean',
        'number_of_purchases': 'mean',
        'total_spending': 'mean'
    }).reset_index()

    segment_stats.columns = ['Segment', 'Customer Count', 'Avg. Days Since Last Purchase', 'Avg. Number of Purchases', 'Avg. Total Spending (R$)']
    st.dataframe(segment_stats, use_container_width=True)

    # Add notes explaining each customer category
    st.markdown("""
    ### Customer Segment Categories:

    - **At Risk**: Customers who have not made a purchase in the last 90 to 180 days. They are showing signs of disengagement and may require re-engagement efforts to bring them back.
    
    - **Inactive Customers**: Customers who have not made any purchases for over 180 days. This segment represents potential lost revenue, and targeted campaigns may be necessary to reactivate their interest.

    - **Loyal Customers**: Customers who regularly shop and have made multiple purchases within the last 60 days. They represent a reliable revenue source and should be nurtured to maintain loyalty and encourage repeat purchases.

    - **New Customers**: Customers who have made their first purchase within the last 90 days. They are in the early stages of their buying journey, and effective onboarding strategies can help convert them into loyal customers.
    """)

    # Collapsible component for conclusion
    with st.expander("Conclusion"):
        st.write("""
        <style>
        .streamlit-expanderHeader {
            border-bottom: none !important;
        }
        .streamlit-expanderContent {
            padding: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.write("""
        <div style='width: 100%;'>
            <p style='text-align: justify;'>
            The customer behavior analysis has revealed five distinct segments that provide valuable insights into purchasing patterns, especially following the significant growth the business experienced from 2016 to early 2018, with peak orders in November 2017 and higher volumes on weekdays. However, the drastic decline observed in Q3-Q4 2018 signals a need for further investigation and corrective actions. By identifying segments such as VIP Customers and Loyal Customers who require tailored engagement strategies, as well as New Customers who need onboarding, and At Risk and Inactive Customers who require re-engagement initiatives, the business can effectively allocate marketing resources to address these challenges and foster sustained growth.            </p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.header("Product Categories Analysis")
    
    # Top product categories
    category_counts = df.groupby('product_category_name_english')['order_id'].count().sort_values(ascending=True)
    
    fig = px.bar(y=category_counts.tail(15).index, x=category_counts.tail(15).values,
                 title='Top 15 Product Categories', orientation='h')
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional distribution of top categories
    top_5_categories = df.groupby('product_category_name_english')['order_id'].count().nlargest(5).index
    regional_dist = df[df['product_category_name_english'].isin(top_5_categories)]
    
    fig = px.bar(regional_dist.groupby(['customer_state', 'product_category_name_english'])['order_id'].count().reset_index(),
                 x='customer_state', y='order_id', color='product_category_name_english',
                 title='Regional Distribution of Top 5 Categories')
    st.plotly_chart(fig, use_container_width=True)

    # Collapsible component for conclusion
    with st.expander("Conclusion"):
        st.write("""
        <style>
        .streamlit-expanderHeader {
            border-bottom: none !important;
        }
        .streamlit-expanderContent {
            padding: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.write("""
        <div style='width: 100%;'>
            <p style='text-align: justify;'>
            The `bed_bath_table` category was the best-selling product category with 11,988 orders, followed by health_beauty and sports_leisure. São Paulo dominated the market with almost half of the total orders, with the `bed_bath_table` category as the best-selling product. Rio de Janeiro and Minas Gerais rounded out the top three regions with varying category preferences. Differences in purchasing patterns between regions indicate the importance of marketing strategies tailored to local preferences, especially in metropolitan areas that show a more diverse distribution of product categories.
            </p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.header("Delivery Analysis")
    
    # Calculate delivery time
    df['delivery_time'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.total_seconds() / (24*60*60)
    
    # Average delivery time by state
    state_delivery = df.groupby('customer_state')['delivery_time'].mean().reset_index()
    
    fig = px.bar(state_delivery, x='customer_state', y='delivery_time',
                 title='Average Delivery Time by State (Days)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Delivery time trends (remove duplicate section)
    monthly_delivery = df.groupby(pd.Grouper(key='order_purchase_timestamp', freq='M'))['delivery_time'].mean().reset_index()
    
    # Filter data from January 2017
    monthly_delivery = monthly_delivery[monthly_delivery['order_purchase_timestamp'] >= '2017-01-01']
    
    fig = px.line(monthly_delivery, x='order_purchase_timestamp', y='delivery_time',
                  title='Average Delivery Time Trends (Days)')
    st.plotly_chart(fig, use_container_width=True)

    # Add hour of order analysis
    df['order_hour'] = df['order_purchase_timestamp'].dt.hour

    # Calculate average delivery time by hour
    hourly_delivery = df.groupby('order_hour')['delivery_time'].mean().reset_index()

    # Visualization
    fig = px.line(hourly_delivery, x='order_hour', y='delivery_time',
                  title='Average Delivery Time by Order Hour',
                  labels={'order_hour': 'Hour of Day', 'delivery_time': 'Average Delivery Time (Days)'})
    fig.update_traces(mode='lines+markers', line=dict(width=2), marker=dict(size=6))
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
    st.plotly_chart(fig, use_container_width=True)

    # Collapsible component for conclusion
    with st.expander("Conclusion"):
        st.write("""
        <style>
        .streamlit-expanderHeader {
            border-bottom: none !important;
        }
        .streamlit-expanderContent {
            padding: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.write("""
        <div style='width: 100%;'>
            <p style='text-align: justify;'>
            Delivery times fluctuate significantly, peaking in September 2017 and reaching their lowest point in August 2017. There are substantial variations in shipping times across Brazilian states, with RR experiencing the longest delays and SP enjoying the shortest delivery periods. Order timing also impacts delivery efficiency, with orders placed at midnight 00:00 taking the longest to fulfill, while those placed at 4:00 AM experiencing the quickest delivery times            </p>
        """, unsafe_allow_html=True)

with tab5:
    st.header("Customer Reviews Analysis")
    
    # Review score distribution
    review_dist = df['review_score'].value_counts().sort_index()
    
    fig = px.pie(values=review_dist.values, names=review_dist.index,
                 title='Distribution of Review Scores',
                 labels={'names': 'Review Score'})  
    st.plotly_chart(fig, use_container_width=True)
    
    # Relationship between delivery time and review score
    avg_delivery_by_score = df.groupby('review_score')['delivery_time'].mean().reset_index()
    
    fig = px.bar(avg_delivery_by_score, x='review_score', y='delivery_time',
                 title='Average Delivery Time by Review Score',
                 labels={'review_score': 'Review Score',  
                        'delivery_time': 'Delivery Time (Days)'} )
    st.plotly_chart(fig, use_container_width=True)

    # Relationship between delivery time and review score (scatter plot)
    delivery_review = df.copy()
    delivery_review['delivery_time'] = (delivery_review['order_delivered_customer_date'] - 
                                        delivery_review['order_purchase_timestamp']).dt.days

    fig = px.scatter(delivery_review, x='delivery_time', y='review_score',
                     title='Relationship Between Delivery Time and Review Score',
                     labels={'delivery_time': 'Delivery Time (Days)', 'review_score': 'Review Score'},
                     opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)

    # Calculate if delivery was on time
    delivery_review['is_on_time'] = delivery_review['order_delivered_customer_date'] <= \
                                delivery_review['order_estimated_delivery_date']

    # Grouped bar plot for on-time vs late deliveries
    on_time_reviews = delivery_review.groupby(['is_on_time', 'review_score']).size().unstack()
    on_time_reviews.index = ['Late Delivery', 'On Time Delivery']

    # Define a sequential color scale for review scores (1-5)
    color_scale = {
        1: 'red',
        2: 'orange',
        3: 'yellow',
        4: 'lightgreen',
        5: 'darkgreen'
    }

    # Create a list of colors in the order of the columns
    colors = [color_scale[score] for score in on_time_reviews.columns]

    fig = px.bar(on_time_reviews, barmode='group',
                title='Review Score Distribution: On-Time vs Late Deliveries',
                labels={'value': 'Number of Reviews', 'is_on_time': 'Delivery Status', 'review_score': 'Review Score'},
                color_discrete_sequence=colors)

    st.plotly_chart(fig, use_container_width=True)


    # Collapsible component for conclusion
    with st.expander("Conclusion"):
        st.write("""
        <style>
        .streamlit-expanderHeader {
            border-bottom: none !important;
        }
        .streamlit-expanderContent {
            padding: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.write("""
        <div style='width: 100%;'>
            <p style='text-align: justify;'>
            Analysis of the distribution of review scores shows that most customers leave positive reviews, with 5 stars dominating (56.2% of total reviews), while there are very few 2-star scores (3.52%). While there was little correlation between delivery time and review scores, customers who received products with long delivery times still left high reviews, indicating that other factors, such as product quality and customer service, also play an important role. On-time deliveries generally received higher review scores, but not all customers were satisfied even though the products were received on time, while late deliveries tended to receive low reviews, although there were still some customers who gave high scores. The average delivery time for 1-star reviews is 19 days, while for 5-star reviews it is 10.6 days, suggesting that shorter delivery times are generally associated with higher review scores.            
            </p>
        """, unsafe_allow_html=True)


