import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Customer Health Dashboard", layout="wide")
st.title("📊 Global E-Commerce Customer Health & Segment Analytics")
st.write("An interactive product analytics portal to track user risk and high-value customer tiers.")

# 2. Load Data
@st.cache_data # Caches data so the app loads instantly
def load_data():
    df = pd.read_csv('ecommerce_customer_analytics.csv')
    
    # Calculate components
    df['value_score'] = pd.qcut(df['total_spent_usd'], 10, labels=False, duplicates='drop') + 1
    df['engagement_score'] = pd.qcut(df['avg_pages_per_session'] * df['avg_session_duration_min'], 10, labels=False, duplicates='drop') + 1
    
    df['satisfaction_score_norm'] = df['satisfaction_score'] * 2
    df['return_penalty'] = pd.qcut(df['return_rate'], 10, labels=False, duplicates='drop')
    
    # Calculate Weighted Health Score
    df['customer_health_score'] = (
        (df['value_score'] * 4) + 
        (df['engagement_score'] * 4) + 
        ((df['satisfaction_score_norm'] - df['return_penalty']).clip(0, 10) * 2)
    )
    
    # Assign Segments
    def assign_segment(score):
        if score >= 80: return 'Champions (VIP)'
        elif score >= 50: return 'Healthy / Active'
        elif score >= 30: return 'At Risk'
        else: return 'Severely Atrophied / Churned'
        
    df['health_segment'] = df['customer_health_score'].apply(assign_segment)
    return df

df = load_data()

# 3. Sidebar Interactive Filters
st.sidebar.header("Filter Analytics")
region_filter = st.sidebar.multiselect("Select Region", options=df['region'].unique(), default=df['region'].unique())
segment_filter = st.sidebar.multiselect("Select Health Segment", options=df['health_segment'].unique(), default=df['health_segment'].unique())

# Apply Filters
filtered_df = df[(df['region'].isin(region_filter)) & (df['health_segment'].isin(segment_filter))]

# 4. Top-level KPIs
st.subheader("📌 Key Growth Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers Displayed", f"{len(filtered_df):,}")
col2.metric("Avg. Health Score", f"{filtered_df['customer_health_score'].mean():.1f} / 100")
col3.metric("Total Revenue", f"${filtered_df['total_spent_usd'].sum():,.2f}")
col4.metric("Avg. Satisfaction Rate", f"{filtered_df['satisfaction_score'].mean():.2f} / 5")

st.markdown("---")

# 5. Interactive Visualizations
st.subheader("🔍 Behavioral & Segmentation Deep Dive")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("### Customer Segment Distribution")
    fig_pie = px.pie(filtered_df, names='health_segment', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_col2:
    st.write("### Health Score vs. Total Spending")
    fig_scatter = px.scatter(filtered_df, x='customer_health_score', y='total_spent_usd', 
                             color='health_segment', hover_data=['customer_id', 'age'])
    st.plotly_chart(fig_scatter, use_container_width=True)

# 6. Raw Data Table / Actionable List Download
st.subheader("📋 Actionable Customer Target List")
st.write("Use the filters on the left to isolate specific cohorts (e.g., 'At Risk' users) and view/export their profiles below:")
st.dataframe(filtered_df[['customer_id', 'region', 'customer_health_score', 'health_segment', 'total_spent_usd', 'newsletter_subscribed']])
