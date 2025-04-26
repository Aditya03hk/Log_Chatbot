import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import time

# DB Connection
def get_connection():
    return sqlite3.connect("logs.db")

# Load logs
@st.cache_data(ttl=30)
def load_logs():
    conn = get_connection()
    access = pd.read_sql("SELECT * FROM access_logs", conn)
    execution = pd.read_sql("SELECT * FROM execution_logs", conn)
    vpc = pd.read_sql("SELECT * FROM vpc_logs", conn)
    conn.close()
    return access, execution, vpc

def main():
    st.set_page_config("AWS Logs Monitoring", layout="wide")
    st.title("📊 AWS Logs Monitoring Dashboard")

    # Sidebar Controls
    st.sidebar.header("Controls")
    live_mode = st.sidebar.toggle("🔄 Live Mode (refresh every 30s)")
    refresh_interval = 30  # seconds

    access_logs, exec_logs, vpc_logs = load_logs()

    # Convert timestamps to datetime
    access_logs["timestamp"] = pd.to_datetime(access_logs["timestamp"])
    exec_logs["timestamp"] = pd.to_datetime(exec_logs["timestamp"])
    vpc_logs["timestamp"] = pd.to_datetime(vpc_logs["timestamp"])

    tab1, tab2, tab3, tab4 = st.tabs(["📄 Overview", "🌐 Access Logs", "⚙️ Execution Logs", "🛡️ VPC Logs"])

    with tab1:
        st.header("Summary Metrics")

        col1, col2, col3 = st.columns(3)
        col1.metric("Access Requests", len(access_logs))
        col2.metric("Function Executions", len(exec_logs))
        col3.metric("VPC Events", len(vpc_logs))

        # Access Methods
        st.subheader("Access Method Distribution")
        method_df = access_logs['method'].value_counts().reset_index()
        method_df.columns = ['method', 'count']
        fig1 = px.pie(method_df, names='method', values='count', title="HTTP Methods")
        st.plotly_chart(fig1, use_container_width=True)

        # Execution Status
        st.subheader("Execution Status")
        status_df = exec_logs['status'].value_counts().reset_index()
        status_df.columns = ['status', 'count']
        fig2 = px.bar(status_df, x='status', y='count', title="Execution Status")
        st.plotly_chart(fig2, use_container_width=True)

        # VPC Actions
        st.subheader("VPC Action Distribution")
        action_df = vpc_logs['action'].value_counts().reset_index()
        action_df.columns = ['action', 'count']
        fig3 = px.bar(action_df, x='action', y='count', title="VPC Actions")
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.header("Access Logs")

        # Filters
        st.subheader("Filter Logs")
        date_range = st.date_input("Select Date Range", [])
        user_filter = st.selectbox("Filter by User ID", ["All"] + sorted(access_logs["user_id"].unique().tolist()))
        filtered = access_logs.copy()

        if len(date_range) == 2:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            filtered = filtered[(filtered["timestamp"] >= start) & (filtered["timestamp"] <= end)]

        if user_filter != "All":
            filtered = filtered[filtered["user_id"] == user_filter]

        st.download_button("📥 Download Filtered Logs", filtered.to_csv(index=False), file_name="access_logs.csv")

        st.dataframe(filtered, use_container_width=True)

        # Charts
        st.subheader("Top Endpoints")
        endpoint_df = filtered["endpoint"].value_counts().head(10).reset_index()
        endpoint_df.columns = ['endpoint', 'count']
        fig4 = px.bar(endpoint_df, x="endpoint", y="count", title="Top Accessed Endpoints")
        st.plotly_chart(fig4, use_container_width=True)

        st.subheader("Status Codes Over Time")
        fig5 = px.scatter(filtered, x="timestamp", y="status_code", color="method",
                          title="Status Codes Timeline")
        st.plotly_chart(fig5, use_container_width=True)

    with tab3:
        st.header("Execution Logs")

        # Filters
        st.subheader("Filter Logs")
        date_range_exec = st.date_input("Select Date Range (Execution)", [])
        function_filter = st.selectbox("Filter by Function", ["All"] + sorted(exec_logs["function_name"].unique().tolist()))
        filtered_exec = exec_logs.copy()

        if len(date_range_exec) == 2:
            start, end = pd.to_datetime(date_range_exec[0]), pd.to_datetime(date_range_exec[1])
            filtered_exec = filtered_exec[(filtered_exec["timestamp"] >= start) & (filtered_exec["timestamp"] <= end)]

        if function_filter != "All":
            filtered_exec = filtered_exec[filtered_exec["function_name"] == function_filter]

        st.download_button("📥 Download Filtered Logs", filtered_exec.to_csv(index=False), file_name="execution_logs.csv")

        st.dataframe(filtered_exec, use_container_width=True)

        # Charts
        st.subheader("Function Duration Distribution")
        fig6 = px.box(filtered_exec, x="function_name", y="duration_ms", color="function_name",
                      title="Function Execution Durations")
        st.plotly_chart(fig6, use_container_width=True)

    with tab4:
        st.header("VPC Logs")

        # Filters
        st.subheader("Filter Logs")
        date_range_vpc = st.date_input("Select Date Range (VPC)", [])
        action_filter = st.selectbox("Filter by Action", ["All"] + sorted(vpc_logs["action"].unique().tolist()))
        filtered_vpc = vpc_logs.copy()

        if len(date_range_vpc) == 2:
            start, end = pd.to_datetime(date_range_vpc[0]), pd.to_datetime(date_range_vpc[1])
            filtered_vpc = filtered_vpc[(filtered_vpc["timestamp"] >= start) & (filtered_vpc["timestamp"] <= end)]

        if action_filter != "All":
            filtered_vpc = filtered_vpc[filtered_vpc["action"] == action_filter]

        st.download_button("📥 Download Filtered Logs", filtered_vpc.to_csv(index=False), file_name="vpc_logs.csv")

        st.dataframe(filtered_vpc, use_container_width=True)

        st.subheader("Top Source IPs by Bytes Sent")
        top_src = filtered_vpc.groupby("src_ip")["bytes_sent"].sum().sort_values(ascending=False).head(10).reset_index()
        top_src.columns = ['src_ip', 'total_bytes_sent']
        fig7 = px.bar(top_src, x="src_ip", y="total_bytes_sent", title="Top Source IPs by Traffic")
        st.plotly_chart(fig7, use_container_width=True)

        st.subheader("Traffic Over Time")
        fig8 = px.line(filtered_vpc, x="timestamp", y="bytes_sent", color="action", title="VPC Traffic Over Time")
        st.plotly_chart(fig8, use_container_width=True)

    # Auto-refresh logic
    if live_mode:
        time.sleep(refresh_interval)
        st.experimental_rerun()

if __name__ == "__main__":
    main()
