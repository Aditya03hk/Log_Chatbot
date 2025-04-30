import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import numpy as np
from typing import List, Tuple

# Database connection
def get_db_connection():
    return sqlite3.connect("logs2.db")

# Helper functions
def run_query(query: str) -> Tuple[List[Tuple], List[str]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return rows, columns
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return [], []
    finally:
        conn.close()

def to_dataframe(rows: List[Tuple], columns: List[str]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=columns)

def get_common_layout(title: str):
    return dict(
        title=dict(text=title, x=0.5, xanchor='center'),
        template="plotly_dark",
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(family="Segoe UI", size=14),
        hoverlabel=dict(bgcolor="black", font_size=13, font_family="Segoe UI"),
        plot_bgcolor="#111111",
        paper_bgcolor="#111111"
    )

# NEW: Alert detection function
def detect_alerts(start_date):
    alerts = []
    
    # Detect high error rates - using -- for comments instead of #
    query = f"""
    SELECT date(timestamp) as day, 
           SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END)*100.0/COUNT(*) as error_rate
    FROM access_logs
    WHERE timestamp >= '{start_date}'
    GROUP BY day
    HAVING error_rate > 10  -- Threshold of 10%
    """
    rows, cols = run_query(query)
    if rows:
        for row in rows:
            alerts.append(f"⚠️ High error rate on {row[0]}: {row[1]:.1f}%")
    
    # Detect latency spikes - using -- for comments here too
    query = f"""
    SELECT date(timestamp) as day, AVG(duration_ms) as avg_latency
    FROM execution_logs
    WHERE timestamp >= '{start_date}'
    GROUP BY day
    HAVING avg_latency > 1000  -- Threshold of 1000ms
    """
    rows, cols = run_query(query)
    if rows:
        for row in rows:
            alerts.append(f"⏱️ High latency on {row[0]}: {row[1]:.0f}ms avg")
    
    return alerts

# NEW: Heatmap visualization
# def display_heatmap(start_date):
#     st.subheader("Activity Heatmap")
    
#     # Hourly activity heatmap
#     query = f"""
#     SELECT 
#         strftime('%H', timestamp) as hour,
#         strftime('%w', timestamp) as weekday,
#         COUNT(*) as count
#     FROM access_logs
#     WHERE timestamp >= '{start_date}'
#     GROUP BY hour, weekday
#     """
#     rows, cols = run_query(query)
#     heat_df = to_dataframe(rows, cols)
    
#     if not heat_df.empty:
#         heat_df = heat_df.pivot(index='weekday', columns='hour', values='count')
#         days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
#         heat_df.index = [days[int(i)] for i in heat_df.index]
        
#         fig = px.imshow(heat_df, 
#                        labels=dict(x="Hour of Day", y="Day of Week", color="Requests"),
#                        x=[f"{h}:00" for h in heat_df.columns],
#                        color_continuous_scale='Viridis')
#         fig.update_layout(**get_common_layout("Hourly Activity Pattern"))
#         st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.warning("No data available for heatmap visualization")



# NEW: User behavior analysis
# def display_user_behavior(start_date):
#     st.subheader("User Behavior Analysis")
    
#     # Top users by activity
#     query = f"""
#     SELECT user_id, COUNT(*) as activity_count
#     FROM access_logs
#     WHERE timestamp >= '{start_date}'
#     GROUP BY user_id
#     ORDER BY activity_count DESC
#     LIMIT 10
#     """
#     rows, cols = run_query(query)
#     user_df = to_dataframe(rows, cols)
    
#     if not user_df.empty:
#         fig1 = px.bar(user_df, x='user_id', y='activity_count',
#                      title='Most Active Users',
#                      color_discrete_sequence=['#636EFA'])
#         fig1.update_layout(**get_common_layout("Most Active Users"))
        
#         # User session analysis
#         query = f"""
#         SELECT user_id, 
#                COUNT(DISTINCT date(timestamp)) as active_days,
#                AVG(strftime('%s', timestamp) - 
#                    LAG(strftime('%s', timestamp)) OVER (PARTITION BY user_id ORDER BY timestamp)) as avg_time_between_requests
#         FROM access_logs
#         WHERE timestamp >= '{start_date}'
#         GROUP BY user_id
#         HAVING active_days > 1
#         LIMIT 10
#         """
#         rows, cols = run_query(query)
#         session_df = to_dataframe(rows, cols)
        
#         if not session_df.empty:
#             fig2 = px.scatter(session_df, x='active_days', y='avg_time_between_requests',
#                             size='avg_time_between_requests', color='user_id',
#                             title='User Engagement Patterns',
#                             hover_name='user_id')
#             fig2.update_layout(**get_common_layout("User Engagement Patterns"))
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.plotly_chart(fig1, use_container_width=True)
#             with col2:
#                 st.plotly_chart(fig2, use_container_width=True)
#         else:
#             st.plotly_chart(fig1, use_container_width=True)
#     else:
#         st.warning("No user behavior data available")

# NEW: Performance benchmarking
def display_performance_benchmarks(start_date):
    st.subheader("Performance Benchmarks")
    
    # Compare current period with previous period
    prev_start = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S') - timedelta(days=7)
    prev_start = prev_start.strftime('%Y-%m-%d %H:%M:%S')
    
    metrics = [
        ("Total Requests", "SELECT COUNT(*) FROM access_logs WHERE timestamp >= '{}'"),
        ("Success Rate", "SELECT SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END)*100.0/COUNT(*) FROM execution_logs WHERE timestamp >= '{}'"),
        ("Avg Latency", "SELECT AVG(duration_ms) FROM execution_logs WHERE timestamp >= '{}'"),
        ("Error Rate", "SELECT SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END)*100.0/COUNT(*) FROM access_logs WHERE timestamp >= '{}'")
    ]
    
    results = []
    for name, query_template in metrics:
        current_query = query_template.format(start_date)
        prev_query = query_template.format(prev_start)
        
        current_val = run_query(current_query)[0][0][0] or 0
        prev_val = run_query(prev_query)[0][0][0] or 0
        
        # change = ((current_val - prev_val) / prev_val * 100) if prev_val != 0 else 0
        results.append((name, current_val))
    
    bench_df = pd.DataFrame(results, columns=['Metric', 'Current'])
    
    # Display metrics with delta indicators
    cols = st.columns(len(metrics))
    for idx, (col, (name, current)) in enumerate(zip(cols, results)):
        # delta = f"{change:.1f}%" if not np.isnan(change) else "N/A"
        col.metric(name, 
                  f"{current:.1f}" if isinstance(current, float) else f"{current:,}")
    
    # Trend comparison chart
    if not bench_df.empty:
        fig = px.bar(bench_df, x='Metric', y=['Current'],
                    barmode='group', title='Performance Comparison',
                    text_auto=True)
        fig.update_layout(**get_common_layout("Performance Benchmarks"))
        st.plotly_chart(fig, use_container_width=True)

def display_kpis(start_date):
    st.subheader("Key Performance Indicators")
    
    # Calculate KPIs
    query = f"""
    SELECT 
        (SELECT COUNT(*) FROM vpc_logs WHERE timestamp >= '{start_date}') as vpc_count,
        (SELECT COUNT(*) FROM access_logs WHERE timestamp >= '{start_date}') as access_count,
        (SELECT COUNT(*) FROM execution_logs WHERE timestamp >= '{start_date}') as exec_count,
        (SELECT COUNT(*) FROM execution_logs WHERE status = 'SUCCESS' AND timestamp >= '{start_date}') as success_count,
        (SELECT COUNT(*) FROM execution_logs WHERE status = 'FAILED' AND timestamp >= '{start_date}') as failed_count,
        (SELECT AVG(duration_ms) FROM execution_logs WHERE timestamp >= '{start_date}') as avg_latency,
        (SELECT COUNT(DISTINCT user_id) FROM access_logs WHERE timestamp >= '{start_date}') as unique_users,
        (SELECT COUNT(DISTINCT src_ip) FROM vpc_logs WHERE timestamp >= '{start_date}') as unique_ips
    """
    rows, cols = run_query(query)
    kpi_df = to_dataframe(rows, cols)
    
    # Handle None values
    vpc_count = kpi_df['vpc_count'][0] or 0
    access_count = kpi_df['access_count'][0] or 0
    exec_count = kpi_df['exec_count'][0] or 0
    success_count = kpi_df['success_count'][0] or 0
    failed_count = kpi_df['failed_count'][0] or 0
    avg_latency = kpi_df['avg_latency'][0] or 0
    unique_users = kpi_df['unique_users'][0] or 0
    unique_ips = kpi_df['unique_ips'][0] or 0
    
    # Calculate success rate safely
    success_rate = (success_count / exec_count * 100) if exec_count > 0 else 0
    
    # Display KPIs with proper null handling
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total VPC Logs", f"{vpc_count:,}")
        st.metric("Total Access Logs", f"{access_count:,}")
    with col2:
        st.metric("Total Executions", f"{exec_count:,}")
        st.metric("Unique Users", f"{unique_users:,}")
    with col3:
        st.metric("Success Rate", f"{success_rate:.1f}%")
        st.metric("Unique IPs", f"{unique_ips:,}")
    with col4:
        st.metric("Failure Count", f"{failed_count:,}")
        st.metric("Avg Latency", f"{avg_latency:.0f} ms" if avg_latency is not None else "N/A")

def display_vpc_analysis(start_date):
    st.subheader("VPC Logs Analysis")
    
    # VPC Actions Distribution
    query = f"""
    SELECT action, COUNT(*) as count 
    FROM vpc_logs 
    WHERE timestamp >= '{start_date}'
    GROUP BY action
    """
    rows, cols = run_query(query)
    action_df = to_dataframe(rows, cols)
    
    fig1 = px.pie(action_df, values='count', names='action', title='VPC Actions Distribution',
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig1.update_layout(**get_common_layout("VPC Actions Distribution"))
    
    # Top Source IPs
    query = f"""
    SELECT src_ip, COUNT(*) as count 
    FROM vpc_logs 
    WHERE timestamp >= '{start_date}'
    GROUP BY src_ip 
    ORDER BY count DESC 
    LIMIT 10
    """
    rows, cols = run_query(query)
    src_ip_df = to_dataframe(rows, cols)
    
    fig2 = px.bar(src_ip_df, x='src_ip', y='count', title='Top Source IPs',
                 color_discrete_sequence=['#636EFA'])
    fig2.update_layout(**get_common_layout("Top Source IPs"))
    
    # Bytes Sent Over Time
    query = f"""
    SELECT date(timestamp) as day, SUM(bytes_sent) as total_bytes 
    FROM vpc_logs 
    WHERE timestamp >= '{start_date}'
    GROUP BY day 
    ORDER BY day
    """
    rows, cols = run_query(query)
    bytes_df = to_dataframe(rows, cols)
    
    fig3 = px.line(bytes_df, x='day', y='total_bytes', title='Bytes Sent Over Time',
                  line_shape='spline', markers=True)
    fig3.update_layout(**get_common_layout("Bytes Sent Over Time"))
    
    # Display charts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)

def display_access_analysis(start_date):
    st.subheader("Access Logs Analysis")
    
    # Status Code Distribution
    query = f"""
    SELECT status_code, COUNT(*) as count 
    FROM access_logs 
    WHERE timestamp >= '{start_date}'
    GROUP BY status_code
    """
    rows, cols = run_query(query)
    status_df = to_dataframe(rows, cols)
    
    fig1 = px.pie(status_df, values='count', names='status_code', title='HTTP Status Code Distribution',
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig1.update_layout(**get_common_layout("HTTP Status Code Distribution"))
    
    # Top Endpoints
    query = f"""
    SELECT endpoint, COUNT(*) as count 
    FROM access_logs 
    WHERE timestamp >= '{start_date}'
    GROUP BY endpoint 
    ORDER BY count DESC 
    LIMIT 10
    """
    rows, cols = run_query(query)
    endpoint_df = to_dataframe(rows, cols)
    
    fig2 = px.bar(endpoint_df, x='endpoint', y='count', title='Most Accessed Endpoints',
                 color_discrete_sequence=['#EF553B'])
    fig2.update_layout(**get_common_layout("Most Accessed Endpoints"))
    
    # Method Distribution
    query = f"""
    SELECT method, COUNT(*) as count 
    FROM access_logs 
    WHERE timestamp >= '{start_date}'
    GROUP BY method
    """
    rows, cols = run_query(query)
    method_df = to_dataframe(rows, cols)
    
    fig3 = px.pie(method_df, values='count', names='method', title='HTTP Method Distribution',
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig3.update_layout(**get_common_layout("HTTP Method Distribution"))
    
    # Display charts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig3, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

def display_execution_analysis(start_date):
    st.subheader("Execution Logs Analysis")
    
    # Success/Failure Distribution
    query = f"""
    SELECT status, COUNT(*) as count 
    FROM execution_logs 
    WHERE timestamp >= '{start_date}'
    GROUP BY status
    """
    rows, cols = run_query(query)
    status_df = to_dataframe(rows, cols)
    
    fig1 = px.pie(status_df, values='count', names='status', title='Execution Status Distribution',
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig1.update_layout(**get_common_layout("Execution Status Distribution"))
    
    # Function Performance
    query = f"""
    SELECT function_name, AVG(duration_ms) as avg_duration, 
           SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as success_count,
           SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed_count
    FROM execution_logs 
    WHERE timestamp >= '{start_date}'
    GROUP BY function_name
    """
    rows, cols = run_query(query)
    func_df = to_dataframe(rows, cols)
    
    fig2 = px.bar(func_df, x='function_name', y='avg_duration', 
                 title='Average Execution Time by Function',
                 color_discrete_sequence=['#00CC96'])
    fig2.update_layout(**get_common_layout("Average Execution Time by Function"))
    
    # Success Rate by Function
    func_df['success_rate'] = func_df['success_count'] / (func_df['success_count'] + func_df['failed_count']) * 100
    fig3 = px.bar(func_df, x='function_name', y='success_rate', 
                 title='Success Rate by Function',
                 color_discrete_sequence=['#AB63FA'])
    fig3.update_layout(**get_common_layout("Success Rate by Function"))
    
    # Display charts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)

def display_correlation_analysis(start_date):
    st.subheader("Correlation Analysis")
    
    # Join all three tables for comprehensive analysis
    query = f"""
    SELECT 
        a.user_id,
        a.endpoint,
        a.status_code,
        v.action as vpc_action,
        v.bytes_sent,
        e.function_name,
        e.duration_ms,
        e.status as exec_status
    FROM access_logs a
    JOIN vpc_logs v ON a.request_id = v.request_id
    JOIN execution_logs e ON a.request_id = e.request_id
    WHERE a.timestamp >= '{start_date}'
    LIMIT 1000
    """
    rows, cols = run_query(query)
    if rows:
        corr_df = to_dataframe(rows, cols)
        
        # Status Code vs VPC Action
        fig1 = px.sunburst(corr_df, path=['status_code', 'vpc_action'], 
                          title='Status Code vs VPC Action',
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        fig1.update_layout(**get_common_layout("Status Code vs VPC Action"))
        
        # Duration by Function and Status
        fig2 = px.box(corr_df, x='function_name', y='duration_ms', color='exec_status',
                     title='Execution Duration by Function and Status',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_layout(**get_common_layout("Execution Duration by Function and Status"))
        
        # Display charts
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No correlation data found for the selected time period.")

def display_trend_analysis(start_date):
    st.subheader("Trend Analysis")
    
    # Requests over time
    query = f"""
    SELECT date(timestamp) as day, COUNT(*) as request_count
    FROM access_logs
    WHERE timestamp >= '{start_date}'
    GROUP BY day
    ORDER BY day
    """
    rows, cols = run_query(query)
    trend_df = to_dataframe(rows, cols)
    
    fig1 = px.line(trend_df, x='day', y='request_count', 
                  title='Daily Request Trend',
                  line_shape='spline', markers=True)
    fig1.update_layout(**get_common_layout("Daily Request Trend"))
    
    # Error rate over time
    query = f"""
    SELECT date(timestamp) as day, 
           SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
           COUNT(*) as total_count
    FROM access_logs
    WHERE timestamp >= '{start_date}'
    GROUP BY day
    ORDER BY day
    """
    rows, cols = run_query(query)
    error_df = to_dataframe(rows, cols)
    error_df['error_rate'] = (error_df['error_count'] / error_df['total_count']) * 100
    
    fig2 = px.line(error_df, x='day', y='error_rate', 
                  title='Daily Error Rate Trend',
                  line_shape='spline', markers=True)
    fig2.update_layout(**get_common_layout("Daily Error Rate Trend"))
    
    # Display charts
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

def display_anomaly_detection(start_date):
    st.subheader("Anomaly Detection")
    
    # 1. Detect unusual error rate spikes
    query = f"""
    SELECT date(timestamp) as day, 
           SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END)*100.0/COUNT(*) as error_rate,
           COUNT(*) as total_requests
    FROM access_logs
    WHERE timestamp >= '{start_date}'
    GROUP BY day
    ORDER BY day
    """
    rows, cols = run_query(query)
    error_df = to_dataframe(rows, cols)
    
    if not error_df.empty:
        # Calculate z-score for error rates
        error_df['error_zscore'] = (error_df['error_rate'] - error_df['error_rate'].mean()) / error_df['error_rate'].std()
        
        # Flag anomalies (z-score > 2)
        anomalies = error_df[error_df['error_zscore'].abs() > 2]
        
        fig1 = px.line(error_df, x='day', y='error_rate', 
                      title='Daily Error Rate with Anomalies',
                      labels={'error_rate': 'Error Rate (%)'},
                      line_shape='spline')
        
        if not anomalies.empty:
            fig1.add_trace(go.Scatter(
                x=anomalies['day'],
                y=anomalies['error_rate'],
                mode='markers',
                marker=dict(color='red', size=10),
                name='Anomaly'
            ))
            for _, row in anomalies.iterrows():
                st.warning(f"⚠️ Anomalous error rate on {row['day']}: {row['error_rate']:.1f}% "
                          f"(Z-score: {row['error_zscore']:.1f}, {row['total_requests']} requests)")
        
        fig1.update_layout(**get_common_layout("Error Rate Anomalies"))
        st.plotly_chart(fig1, use_container_width=True)
    
    # 2. Detect unusual latency patterns
    query = f"""
    SELECT date(timestamp) as day, function_name,
           AVG(duration_ms) as avg_latency,
           COUNT(*) as executions
    FROM execution_logs
    WHERE timestamp >= '{start_date}'
    GROUP BY day, function_name
    ORDER BY day
    """
    rows, cols = run_query(query)
    latency_df = to_dataframe(rows, cols)
    
    if not latency_df.empty:
        # Calculate z-score per function
        latency_df['latency_zscore'] = latency_df.groupby('function_name')['avg_latency'].transform(
            lambda x: (x - x.mean()) / x.std()
        )
        
        # Flag anomalies (z-score > 2)
        latency_anomalies = latency_df[latency_df['latency_zscore'].abs() > 2]
        
        fig2 = px.line(latency_df, x='day', y='avg_latency', color='function_name',
                      title='Daily Latency by Function with Anomalies',
                      labels={'avg_latency': 'Average Latency (ms)'},
                      line_shape='spline')
        
        if not latency_anomalies.empty:
            fig2.add_trace(go.Scatter(
                x=latency_anomalies['day'],
                y=latency_anomalies['avg_latency'],
                mode='markers',
                marker=dict(color='red', size=10),
                name='Anomaly'
            ))
            for _, row in latency_anomalies.iterrows():
                st.error(f"⏱️ Latency anomaly for {row['function_name']} on {row['day']}: "
                        f"{row['avg_latency']:.0f}ms (Z-score: {row['latency_zscore']:.1f}, "
                        f"{row['executions']} executions)")
        
        fig2.update_layout(**get_common_layout("Latency Anomalies"))
        st.plotly_chart(fig2, use_container_width=True)
    
    # 3. Unusual traffic patterns
    query = f"""
    SELECT strftime('%H', timestamp) as hour, COUNT(*) as requests
    FROM access_logs
    WHERE timestamp >= '{start_date}'
    GROUP BY hour
    ORDER BY hour
    """
    rows, cols = run_query(query)
    traffic_df = to_dataframe(rows, cols)
    
    if not traffic_df.empty:
        # Calculate typical pattern (median per hour)
        traffic_df['typical'] = traffic_df['requests'].median()
        traffic_df['deviation'] = (traffic_df['requests'] - traffic_df['typical']) / traffic_df['typical'] * 100
        
        # Flag anomalies (>50% deviation from typical)
        traffic_anomalies = traffic_df[traffic_df['deviation'].abs() > 50]
        
        fig3 = px.bar(traffic_df, x='hour', y='requests',
                     title='Hourly Traffic Pattern with Anomalies',
                     labels={'hour': 'Hour of Day', 'requests': 'Number of Requests'})
        
        if not traffic_anomalies.empty:
            fig3.add_trace(go.Scatter(
                x=traffic_anomalies['hour'],
                y=traffic_anomalies['requests'],
                mode='markers',
                marker=dict(color='red', size=10),
                name='Anomaly'
            ))
            for _, row in traffic_anomalies.iterrows():
                st.info(f"📈 Traffic anomaly at {row['hour']}:00 - {row['requests']} requests "
                       f"({row['deviation']:+.0f}% from typical)")
        
        fig3.update_layout(**get_common_layout("Traffic Pattern Anomalies"))
        st.plotly_chart(fig3, use_container_width=True)

# Dashboard layout with new features
def setup_dashboard():
    st.set_page_config(layout="wide", page_title="Log Analysis Dashboard", page_icon="📊")
    st.title("Log Analysis Dashboard")
    
    # Sidebar filters with date range picker
    st.sidebar.title("Filters")
    time_range = st.sidebar.selectbox("Time Range", 
                                    ["Last 24 hours", "Last 7 days", "Last 30 days", "Custom Range"])
    
    if time_range == "Custom Range":
        col1, col2 = st.sidebar.columns(2)
        start_date = col1.date_input("Start Date", datetime.now() - timedelta(days=7))
        end_date = col2.date_input("End Date", datetime.now())
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.max.time())
    else:
        now = datetime.now()
        if time_range == "Last 24 hours":
            start_date = now - timedelta(days=1)
        elif time_range == "Last 7 days":
            start_date = now - timedelta(days=7)
        elif time_range == "Last 30 days":
            start_date = now - timedelta(days=30)
        else:
            start_date = datetime.min
        end_date = now
    
    return start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S')

# Main app with new features
def main():
    start_date, end_date = setup_dashboard()
    
    # Display alerts at the top
    alerts = detect_alerts(start_date)
    if alerts:
        with st.expander("🚨 Active Alerts", expanded=True):
            for alert in alerts:
                st.warning(alert)
    
    # Create tabs for different sections
    tab_names = [
        "Overview", "VPC Logs", "Access Logs", "Execution Logs", 
        "Trends", "Anomalies", "Benchmarks"
    ]
   
    tabs = st.tabs(tab_names)
    
    with tabs[0]:  # Overview
        display_kpis(start_date)
        display_correlation_analysis(start_date)
        # display_heatmap(start_date)
    
    with tabs[1]:  # VPC Logs
        display_vpc_analysis(start_date)
    
    with tabs[2]:  # Access Logs
        display_access_analysis(start_date)
    
    with tabs[3]:  # Execution Logs
        display_execution_analysis(start_date)
    
    with tabs[4]:  # Trends
        display_trend_analysis(start_date)
    
    with tabs[5]:  # Anomalies
        display_anomaly_detection(start_date)
    
    # with tabs[6]:  # User Behavior
    #     display_user_behavior(start_date)
    
    
    with tabs[6]:  # Benchmarks
        display_performance_benchmarks(start_date)

if __name__ == "__main__":
    main()


