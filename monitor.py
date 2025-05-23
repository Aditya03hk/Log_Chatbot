
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import sqlite3
# from datetime import datetime, timedelta
# import numpy as np
# from typing import Tuple, Optional, Dict, Any
# import time

# # ==============================================
# # CONFIGURATION AND CONSTANTS
# # ==============================================
# st.set_page_config(
#     layout="wide", 
#     page_title="Cloud Log Analytics Dashboard", 
#     page_icon="📊",
#     initial_sidebar_state="expanded"
# )

# DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
# DEFAULT_DATE_RANGE = ("Last 7 days", 7)

# THEME = {
#     "colors": px.colors.qualitative.Plotly,
#     "template": "plotly_dark",
#     "layout": {
#         "margin": dict(l=20, r=20, t=60, b=20),
#         "font": dict(family="Segoe UI", size=12),
#         "plot_bgcolor": "#0E1117",
#         "paper_bgcolor": "#0E1117",
#         "hoverlabel": dict(bgcolor="#1F2C40", font_size=12)
#     }
# }

# # ==============================================
# # DATABASE UTILITIES
# # ==============================================
# @st.cache_resource(ttl=3600)
# def get_db_connection(max_retries: int = 3) -> sqlite3.Connection:
#     """Create and cache database connection with retry logic"""
#     for attempt in range(max_retries):
#         try:
#             conn = sqlite3.connect("logs2.db", check_same_thread=False)
#             conn.row_factory = sqlite3.Row
#             # Enable window functions
#             conn.execute("PRAGMA recursive_triggers = ON")
#             # Test connection immediately
#             conn.execute("SELECT 1").fetchone()
#             return conn
#         except sqlite3.Error as e:
#             if attempt == max_retries - 1:
#                 st.error(f"❌ Failed to connect to database after {max_retries} attempts: {str(e)}")
#                 st.stop()
#             time.sleep(1)

# def run_query(_conn: sqlite3.Connection, query: str, params: tuple = ()) -> pd.DataFrame:
#     """Execute SQL query and return results as DataFrame"""
#     try:
#         if _conn is None:
#             raise ValueError("Database connection is not available")
#         return pd.read_sql_query(query, _conn, params=params).replace({np.nan: None})
#     except Exception as e:
#         st.error(f"❌ Query execution failed: {str(e)}")
#         return pd.DataFrame()

# def safe_get_first_row(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
#     """Safely get first row of DataFrame or return None if empty"""
#     return dict(df.iloc[0]) if not df.empty else None

# # ==============================================
# # UI COMPONENTS
# # ==============================================
# def date_selector() -> Tuple[str, str]:
#     """Create date range selector in sidebar"""
#     st.sidebar.header("📅 Date Range Selector")
    
#     date_options = {
#         "Last 1 hour": 1/24,
#         "Last 6 hours": 6/24,
#         "Last 12 hours": 12/24,
#         "Last 24 hours": 1,
#         "Last 7 days": 7,
#         "Last 30 days": 30,
#         "Custom Range": None
#     }
    
#     selected_option = st.sidebar.selectbox(
#         "Select time range", 
#         list(date_options.keys()),
#         index=list(date_options.keys()).index(DEFAULT_DATE_RANGE[0])
#     )
    
#     if date_options[selected_option] is not None:
#         days = date_options[selected_option]
#         start_date = datetime.now() - timedelta(days=days)
#         end_date = datetime.now()
#     else:
#         col1, col2 = st.sidebar.columns(2)
#         start_date = col1.date_input("Start date", datetime.now() - timedelta(days=DEFAULT_DATE_RANGE[1]))
#         end_date = col2.date_input("End date", datetime.now())
    
#     start_dt = datetime.combine(start_date, datetime.min.time())
#     end_dt = datetime.combine(end_date, datetime.max.time())
    
#     st.sidebar.caption(f"Selected range: {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%Y-%m-%d %H:%M')}")
#     return start_dt.strftime(DATE_FORMAT), end_dt.strftime(DATE_FORMAT)

# def display_metrics(metrics: Optional[Dict[str, Any]]) -> None:
#     """Display key metrics in columns"""
#     if not metrics:
#         st.warning("⚠️ No metrics data available for selected period")
#         return
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     col1.metric(
#         "📊 Total Requests", 
#         f"{metrics.get('total_requests', 0):,}", 
#         help="Total HTTP requests in selected period"
#     )
    
#     col2.metric(
#         "⏱️ Avg Latency", 
#         f"{metrics.get('avg_latency', 0):.1f} ms", 
#         delta_color="inverse", 
#         help="Average request processing time"
#     )
    
#     col3.metric(
#         "👥 Active Users", 
#         f"{metrics.get('active_users', 0):,}", 
#         help="Unique users with activity"
#     )
    
#     col4.metric(
#         "✅ Success Rate", 
#         f"{metrics.get('success_rate', 0):.1f}%", 
#         help="Percentage of successful executions"
#     )

# # ==============================================
# # VISUALIZATION COMPONENTS
# # ==============================================
# def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str) -> Optional[go.Figure]:
#     """Create styled bar chart with consistent theming"""
#     if df.empty or x not in df.columns or y not in df.columns:
#         return None
        
#     fig = px.bar(
#         df, 
#         x=x, 
#         y=y, 
#         title=title,
#         color_discrete_sequence=THEME["colors"],
#         text=y
#     )
#     fig.update_layout(**THEME["layout"])
#     fig.update_xaxes(type='category')
#     fig.update_traces(texttemplate='%{text:,}', textposition='outside')
#     return fig

# def create_timeseries(df: pd.DataFrame, x: str, y: str, title: str) -> Optional[go.Figure]:
#     """Create time series plot with trendline"""
#     if df.empty or x not in df.columns or y not in df.columns:
#         return None
        
#     fig = px.line(
#         df, 
#         x=x, 
#         y=y, 
#         title=title, 
#         line_shape="spline", 
#         markers=True,
#         color_discrete_sequence=THEME["colors"]
#     )
#     fig.update_layout(**THEME["layout"])
#     fig.update_traces(line=dict(width=2))
    
#     if len(df) > 7:  # Only add trendline if enough data points
#         fig.add_trace(go.Scatter(
#             x=df[x], 
#             y=df[y].rolling(7, min_periods=1).mean(),
#             name='7-day Avg',
#             line=dict(color='#FFA15A', dash='dot')
#         ))
#     return fig

# # ==============================================
# # CORE DASHBOARD SECTIONS
# # ==============================================
# def system_health_overview(conn: sqlite3.Connection, start_date: str, end_date: str) -> None:
#     """Display key system health metrics and trends"""
#     st.header("📈 System Overview")
    
#     # Real-time metrics
#     query = """
#     SELECT 
#         (SELECT COUNT(*) FROM access_logs WHERE timestamp BETWEEN ? AND ?) as total_requests,
#         (SELECT AVG(duration_ms) FROM execution_logs WHERE timestamp BETWEEN ? AND ?) as avg_latency,
#         (SELECT COUNT(DISTINCT user_id) FROM access_logs WHERE timestamp BETWEEN ? AND ?) as active_users,
#         (SELECT 100.0 * SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) / COUNT(*) 
#          FROM execution_logs WHERE timestamp BETWEEN ? AND ?) as success_rate
#     """
#     params = (start_date, end_date) * 4
#     metrics_df = run_query(conn, query, params)
#     metrics = safe_get_first_row(metrics_df)
#     display_metrics(metrics)
    
#     # Trend visualization
#     with st.expander("📅 Trends Over Time", expanded=True):
#         query = """
#         SELECT 
#             strftime('%Y-%m-%d', a.timestamp) as date,
#             COUNT(*) as requests,
#             AVG(e.duration_ms) as latency,
#             100.0 * SUM(CASE WHEN a.status_code < 400 THEN 1 ELSE 0 END) / COUNT(*) as success_rate
#         FROM access_logs a
#         LEFT JOIN execution_logs e ON a.request_id = e.request_id
#         WHERE a.timestamp BETWEEN ? AND ?
#         GROUP BY date
#         ORDER BY date
#         """
#         trend_data = run_query(conn, query, (start_date, end_date))
        
#         if not trend_data.empty:
#             col1, col2 = st.columns(2)
#             with col1:
#                 fig = create_timeseries(trend_data, 'date', 'requests', 'Request Volume')
#                 if fig:
#                     st.plotly_chart(fig, use_container_width=True)
#                 else:
#                     st.warning("Insufficient data for request trend")
            
#             with col2:
#                 fig = create_timeseries(trend_data, 'date', 'latency', 'Latency Trend')
#                 if fig:
#                     st.plotly_chart(fig, use_container_width=True)
#                 else:
#                     st.warning("Insufficient data for latency trend")
            
#             fig = create_timeseries(trend_data, 'date', 'success_rate', 'Success Rate Trend')
#             if fig:
#                 st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.warning("⚠️ No trend data available for selected period")

# def performance_analysis(conn: sqlite3.Connection, start_date: str, end_date: str) -> None:
#     """Analyze system performance metrics"""
#     st.header("⚡ Performance Analysis")
    
#     with st.expander("🔍 Function Performance", expanded=True):
#         query = """
#         SELECT 
#             function_name,
#             COUNT(*) as executions,
#             AVG(duration_ms) as avg_duration,
#             MAX(duration_ms) as max_duration,
#             100.0 * SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) / COUNT(*) as success_rate
#         FROM execution_logs
#         WHERE timestamp BETWEEN ? AND ?
#         GROUP BY function_name
#         ORDER BY executions DESC
#         """
#         perf_data = run_query(conn, query, (start_date, end_date))
        
#         if not perf_data.empty:
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 st.subheader("Execution Volume")
#                 fig = create_bar_chart(
#                     perf_data.head(10), 
#                     'function_name', 
#                     'executions', 
#                     'Top Functions by Execution Count'
#                 )
#                 if fig:
#                     st.plotly_chart(fig, use_container_width=True)
            
#             with col2:
#                 st.subheader("Performance Characteristics")
#                 fig = px.scatter(
#                     perf_data,
#                     x='avg_duration',
#                     y='success_rate',
#                     size='executions',
#                     color='function_name',
#                     hover_name='function_name',
#                     log_x=True,
#                     labels={
#                         'avg_duration': 'Average Duration (ms)',
#                         'success_rate': 'Success Rate (%)'
#                     }
#                 )
#                 fig.update_layout(**THEME["layout"])
#                 st.plotly_chart(fig, use_container_width=True)
            
#             st.subheader("Detailed Performance Metrics")
#             st.dataframe(
#                 perf_data.assign(
#                     avg_duration=lambda x: x['avg_duration'].round(1).astype(str) + " ms",
#                     success_rate=lambda x: x['success_rate'].round(1).astype(str) + "%",
#                     executions=lambda x: x['executions'].apply("{:,}".format)
#                 ),
#                 height=400,
#                 use_container_width=True
#             )
#         else:
#             st.warning("⚠️ No performance data available for selected period")

# def security_analysis(conn: sqlite3.Connection, start_date: str, end_date: str) -> None:
#     """Analyze security-related patterns and anomalies"""
#     st.header("🔒 Security Analysis")
    
#     with st.expander("🛡️ Suspicious Activity", expanded=True):
#         query = """
#         SELECT 
#             v.src_ip,
#             COUNT(*) as request_count,
#             SUM(CASE WHEN a.status_code >= 400 THEN 1 ELSE 0 END) as errors,
#             COUNT(DISTINCT a.user_id) as users_affected,
#             100.0 * SUM(CASE WHEN a.status_code >= 400 THEN 1 ELSE 0 END) / COUNT(*) as error_rate
#         FROM vpc_logs v
#         JOIN access_logs a ON v.request_id = a.request_id
#         WHERE v.timestamp BETWEEN ? AND ?
#         GROUP BY v.src_ip
#         HAVING request_count > 10
#         ORDER BY error_rate DESC
#         LIMIT 20
#         """
#         ips = run_query(conn, query, (start_date, end_date))
        
#         if not ips.empty:
#             col1, col2 = st.columns([1, 2])
            
#             with col1:
#                 st.subheader("Top Suspicious IPs")
#                 st.dataframe(
#                     ips.assign(
#                         request_count=lambda x: x['request_count'].apply("{:,}".format),
#                         error_rate=lambda x: x['error_rate'].round(1).astype(str) + "%",
#                         users_affected=lambda x: x['users_affected'].apply("{:,}".format)
#                     ),
#                     height=500,
#                     use_container_width=True
#                 )
            
#             with col2:
#                 st.subheader("Threat Profile Analysis")
#                 fig = px.scatter(
#                     ips,
#                     x='request_count',
#                     y='error_rate',
#                     size='users_affected',
#                     color='src_ip',
#                     hover_name='src_ip',
#                     log_x=True,
#                     labels={
#                         'request_count': 'Total Requests',
#                         'error_rate': 'Error Rate (%)',
#                         'users_affected': 'Users Affected'
#                     }
#                 )
#                 fig.update_layout(**THEME["layout"])
#                 st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.info("🛈 No suspicious activity detected in selected period")

# def operational_insights(conn: sqlite3.Connection, start_date: str, end_date: str) -> None:
#     """Provide operational business intelligence"""
#     st.header("📊 Operational Insights")
    
#     with st.expander("👥 User Behavior Analysis", expanded=True):
#         # First get the user activity data
#         query = """
#         SELECT
#             user_id,
#             COUNT(DISTINCT date(timestamp)) as active_days,
#             COUNT(*) as total_requests
#         FROM access_logs
#         WHERE timestamp BETWEEN ? AND ?
#         GROUP BY user_id
#         HAVING active_days > 1 AND total_requests > 10
#         ORDER BY total_requests DESC
#         LIMIT 50
#         """
#         users = run_query(conn, query, (start_date, end_date))
        
#         if not users.empty:
#             # Now get the raw timestamp data for these users
#             time_query = """
#             SELECT 
#                 user_id,
#                 timestamp
#             FROM access_logs
#             WHERE user_id IN ({})
#             AND timestamp BETWEEN ? AND ?
#             ORDER BY user_id, timestamp
#             """.format(','.join(['?']*len(users['user_id'])))
            
#             time_params = tuple(users['user_id']) + (start_date, end_date)
#             time_data = run_query(conn, time_query, time_params)
            
#             if not time_data.empty:
#                 # Convert timestamps to datetime objects
#                 time_data['timestamp'] = pd.to_datetime(time_data['timestamp'])
                
#                 # Calculate time differences in seconds
#                 time_data['time_diff'] = time_data.groupby('user_id')['timestamp'].diff().dt.total_seconds()
                
#                 # Calculate average time between requests for each user
#                 avg_times = time_data.groupby('user_id')['time_diff'].mean().reset_index()
#                 avg_times.columns = ['user_id', 'avg_time_between_requests']
                
#                 # Merge with original user data
#                 users = pd.merge(users, avg_times, on='user_id', how='left')
            
#             st.subheader("User Engagement Patterns")
            
#             tab1, tab2 = st.tabs(["Scatter Matrix", "Top Users"])
            
#             with tab1:
#                 if 'avg_time_between_requests' in users.columns:
#                     fig = px.scatter_matrix(
#                         users,
#                         dimensions=['active_days', 'total_requests', 'avg_time_between_requests'],
#                         color='active_days',
#                         hover_name='user_id',
#                         labels={
#                             'active_days': 'Active Days',
#                             'total_requests': 'Total Requests',
#                             'avg_time_between_requests': 'Avg Time Between Requests (sec)'
#                         }
#                     )
#                     fig.update_layout(**THEME["layout"])
#                     st.plotly_chart(fig, use_container_width=True)
#                 else:
#                     st.warning("Could not calculate time between requests")
            
#             with tab2:
#                 display_df = users.copy()
#                 if 'avg_time_between_requests' in display_df.columns:
#                     display_df['avg_time_between_requests'] = display_df['avg_time_between_requests'].round(1).astype(str) + " sec"
#                 display_df['total_requests'] = display_df['total_requests'].apply("{:,}".format)
                
#                 st.dataframe(
#                     display_df,
#                     height=500,
#                     use_container_width=True
#                 )
#         else:
#             st.warning("⚠️ No user behavior data available for selected period")

# # ==============================================
# # MAIN APPLICATION
# # ==============================================
# def main():
#     """Main application entry point"""
#     try:
#         # Get cached database connection
#         conn = get_db_connection()
        
#         # Verify connection is working
#         test_df = run_query(conn, "SELECT name FROM sqlite_master WHERE type='table'")
#         if test_df.empty:
#             st.error("❌ No tables found in database. Please verify your database setup.")
#             st.stop()
        
#         st.sidebar.success(f"Connected to database with {len(test_df)} tables")
        
#         # Get date range
#         start_date, end_date = date_selector()
        
#         # Dashboard layout
#         system_health_overview(conn, start_date, end_date)
#         st.markdown("---")
        
#         # Performance Analysis
#         performance_analysis(conn, start_date, end_date)
        
#         st.markdown("---")
        
#         # Security Analysis below Performance
#         security_analysis(conn, start_date, end_date)
        
#         st.markdown("---")
        
#         operational_insights(conn, start_date, end_date)
        
#     except Exception as e:
#         st.error(f"❌ Critical application error: {str(e)}")
#         st.stop()

# if __name__ == "__main__":
#     main()




import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import numpy as np
from typing import Tuple, Optional, Dict, Any, List
import time
from enum import Enum

# ==============================================
# ENUMS AND CONSTANTS
# ==============================================
class TimeRange(Enum):
    LAST_1H = ("Last 1 hour", 1/24)
    LAST_6H = ("Last 6 hours", 6/24)
    LAST_12H = ("Last 12 hours", 12/24)
    LAST_24H = ("Last 24 hours", 1)
    LAST_7D = ("Last 7 days", 7)
    LAST_30D = ("Last 30 days", 30)
    CUSTOM = ("Custom Range", None)

class AlertLevel(Enum):
    CRITICAL = ("🔴 Critical", "#FF2B2B")
    HIGH = ("🟠 High", "#FFA500")
    MEDIUM = ("🟡 Medium", "#FFCC00")
    LOW = ("🔵 Low", "#1C83E1")
    INFO = ("⚪ Info", "#808080")

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_DATE_RANGE = TimeRange.LAST_7D

# ==============================================
# THEME CONFIGURATION
# ==============================================
def configure_theme():
    pass
    # st.set_page_config(
    #     layout="wide", 
    #     page_title="Cloud Log Analytics Dashboard", 
    #     page_icon="📊",
    #     initial_sidebar_state="expanded"
    # )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
        .metric-card {
            background-color: #1F2C40;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .metric-title {
            font-size: 14px;
            color: #A0AEC0;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: white;
        }
        .alert-card {
            border-left: 4px solid;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        .stDataFrame {
            border-radius: 8px;
        }
        .stAlert {
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

# ==============================================
# DATABASE UTILITIES
# ==============================================
@st.cache_resource(ttl=3600)
def get_db_connection(max_retries: int = 3) -> sqlite3.Connection:
    """Create and cache database connection with retry logic"""
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect("logs2.db", check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA recursive_triggers = ON")
            conn.execute("SELECT 1").fetchone()
            return conn
        except sqlite3.Error as e:
            if attempt == max_retries - 1:
                st.error(f"❌ Failed to connect to database after {max_retries} attempts: {str(e)}")
                st.stop()
            time.sleep(1)

def run_query(_conn: sqlite3.Connection, query: str, params: tuple = ()) -> pd.DataFrame:
    """Execute SQL query and return results as DataFrame"""
    try:
        return pd.read_sql_query(query, _conn, params=params).replace({np.nan: None})
    except Exception as e:
        st.error(f"❌ Query execution failed: {str(e)}")
        return pd.DataFrame()

def safe_get_first_row(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Safely get first row of DataFrame or return None if empty"""
    return dict(df.iloc[0]) if not df.empty else None

# ==============================================
# UI COMPONENTS
# ==============================================
def date_selector() -> Tuple[str, str]:
    """Create date range selector in sidebar"""
    st.sidebar.header("📅 Date Range Selector")
    
    selected_option = st.sidebar.selectbox(
        "Select time range", 
        [tr.value[0] for tr in TimeRange],
        index=[tr.value[0] for tr in TimeRange].index(DEFAULT_DATE_RANGE.value[0]))
    
    if selected_option != TimeRange.CUSTOM.value[0]:
        days = next(tr.value[1] for tr in TimeRange if tr.value[0] == selected_option)
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()
    else:
        col1, col2 = st.sidebar.columns(2)
        start_date = col1.date_input("Start date", datetime.now() - timedelta(days=DEFAULT_DATE_RANGE.value[1]))
        end_date = col2.date_input("End date", datetime.now())
    
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    
    st.sidebar.caption(f"Selected range: {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%Y-%m-%d %H:%M')}")
    return start_dt.strftime(DATE_FORMAT), end_dt.strftime(DATE_FORMAT)

def display_metric_card(title: str, value: Any, delta: str = None, help_text: str = None):
    """Display a metric card with consistent styling"""
    delta_html = f'<div style="font-size: 14px; color: #A0AEC0;">{delta}</div>' if delta else ''
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)
    
    if help_text:
        st.markdown(f'<div style="font-size: 12px; color: #718096;">{help_text}</div>', unsafe_allow_html=True)

def display_alert(level: AlertLevel, title: str, description: str):
    """Display an alert notification"""
    st.markdown(f"""
    <div class="alert-card" style="background-color: #1F2C40; border-color: {level.value[1]}">
        <div style="font-weight: bold; color: {level.value[1]}">{level.value[0]} {title}</div>
        <div style="color: #A0AEC0">{description}</div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================
# VISUALIZATION COMPONENTS
# ==============================================
def create_time_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str = None) -> Optional[go.Figure]:
    """Create time series chart with consistent theming"""
    if df.empty or x not in df.columns or y not in df.columns:
        return None
        
    fig = px.line(
        df, 
        x=x, 
        y=y, 
        title=title,
        color=color,
        line_shape="spline",
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(family="Segoe UI", size=12),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        hoverlabel=dict(bgcolor="#1F2C40", font_size=12)
    )
    
    if len(df) > 7:  # Add trendline if enough data points
        fig.add_trace(go.Scatter(
            x=df[x], 
            y=df[y].rolling(7, min_periods=1).mean(),
            name='7-day Avg',
            line=dict(color='#FFA15A', dash='dot')
        ))
    return fig

def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str = None) -> Optional[go.Figure]:
    """Create bar chart with consistent theming"""
    if df.empty or x not in df.columns or y not in df.columns:
        return None
        
    fig = px.bar(
        df, 
        x=x, 
        y=y, 
        title=title,
        color=color,
        text=y,
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(family="Segoe UI", size=12),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        hoverlabel=dict(bgcolor="#1F2C40", font_size=12)
    )
    
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    return fig

def create_pie_chart(df: pd.DataFrame, names: str, values: str, title: str) -> Optional[go.Figure]:
    """Create pie/donut chart with consistent theming"""
    if df.empty or names not in df.columns or values not in df.columns:
        return None
        
    fig = px.pie(
        df,
        names=names,
        values=values,
        title=title,
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(family="Segoe UI", size=12),
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        hoverlabel=dict(bgcolor="#1F2C40", font_size=12)
    )
    
    return fig

# ==============================================
# DASHBOARD SECTIONS
# ==============================================
def system_health_overview(conn: sqlite3.Connection, start_date: str, end_date: str) -> None:
    """Display key system health metrics and trends"""
    st.header("📈 System Health Overview")
    
    # Get system metrics
    query = """
    SELECT 
        (SELECT COUNT(*) FROM access_logs WHERE timestamp BETWEEN ? AND ?) as total_requests,
        (SELECT AVG(duration_ms) FROM execution_logs WHERE timestamp BETWEEN ? AND ?) as avg_latency,
        (SELECT COUNT(DISTINCT user_id) FROM access_logs WHERE timestamp BETWEEN ? AND ?) as active_users,
        (SELECT 100.0 * SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) / COUNT(*) 
         FROM execution_logs WHERE timestamp BETWEEN ? AND ?) as success_rate,
        (SELECT COUNT(*) FROM vpc_logs WHERE action = 'REJECT' AND timestamp BETWEEN ? AND ?) as rejected_connections,
        (SELECT COUNT(*) FROM execution_logs WHERE status = 'FAILED' AND timestamp BETWEEN ? AND ?) as failed_executions
    """
    params = (start_date, end_date) * 6
    metrics_df = run_query(conn, query, params)
    metrics = safe_get_first_row(metrics_df)
    
    # Display metrics in cards
    col1, col2, col3 = st.columns(3)
    with col1:
        display_metric_card("📊 Total Requests", f"{metrics.get('total_requests', 0):,}", 
                      help_text="Total HTTP requests in selected period")
        display_metric_card("⏱️ Avg Latency", f"{metrics.get('avg_latency', 0):.1f} ms", 
                      help_text="Average request processing time")

    with col2:
        display_metric_card("👥 Active Users", f"{metrics.get('active_users', 0):,}", 
                      help_text="Unique users with activity")
        display_metric_card("✅ Success Rate", f"{metrics.get('success_rate', 0):.1f}%", 
                      help_text="Percentage of successful executions")

    with col3:
        display_metric_card("🚫 Rejected Connections", f"{metrics.get('rejected_connections', 0):,}", 
                      help_text="VPC connections that were rejected")
        display_metric_card("❌ Failed Executions", f"{metrics.get('failed_executions', 0):,}", 
                      help_text="Function executions that failed")
    
    # Alerts section
    st.subheader("🚨 Recent Alerts")
    query = """
    SELECT 
        v.src_ip,
        COUNT(*) as request_count,
        SUM(CASE WHEN a.status_code >= 400 THEN 1 ELSE 0 END) as errors,
        COUNT(DISTINCT a.user_id) as users_affected,
        100.0 * SUM(CASE WHEN a.status_code >= 400 THEN 1 ELSE 0 END) / COUNT(*) as error_rate
    FROM vpc_logs v
    JOIN access_logs a ON v.request_id = a.request_id
    WHERE v.timestamp BETWEEN ? AND ?
    GROUP BY v.src_ip
    HAVING request_count > 10 AND error_rate > 20
    ORDER BY error_rate DESC
    LIMIT 5
    """
    alerts = run_query(conn, query, (start_date, end_date))
    
    if not alerts.empty:
        for _, row in alerts.iterrows():
            if row['error_rate'] > 50:
                level = AlertLevel.CRITICAL
            elif row['error_rate'] > 30:
                level = AlertLevel.HIGH
            else:
                level = AlertLevel.MEDIUM
                
            display_alert(
                level,
                f"Suspicious activity from {row['src_ip']}",
                f"{row['error_rate']:.1f}% error rate across {row['request_count']} requests affecting {row['users_affected']} users"
            )
    else:
        st.info("🎉 No critical alerts detected in the selected time period")
    
    # Trend visualization
    with st.expander("📊 Trends Over Time", expanded=True):
        query = """
        SELECT 
            strftime('%Y-%m-%d', a.timestamp) as date,
            COUNT(*) as requests,
            AVG(e.duration_ms) as latency,
            100.0 * SUM(CASE WHEN a.status_code < 400 THEN 1 ELSE 0 END) / COUNT(*) as success_rate,
            COUNT(DISTINCT a.user_id) as daily_users
        FROM access_logs a
        LEFT JOIN execution_logs e ON a.request_id = e.request_id
        WHERE a.timestamp BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
        """
        trend_data = run_query(conn, query, (start_date, end_date))
        
        if not trend_data.empty:
            tab1, tab2 = st.tabs(["Request Metrics", "User Engagement"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    fig = create_time_chart(trend_data, 'date', 'requests', 'Request Volume')
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = create_time_chart(trend_data, 'date', 'latency', 'Latency Trend')
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                fig = create_time_chart(trend_data, 'date', 'success_rate', 'Success Rate Trend')
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = create_time_chart(trend_data, 'date', 'daily_users', 'Daily Active Users')
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No trend data available for selected period")

def performance_analysis(conn: sqlite3.Connection, start_date: str, end_date: str) -> None:
    """Analyze system performance metrics"""
    st.header("⚡ Performance Analysis")
    
    with st.expander("🔍 Endpoint Performance", expanded=True):
        query = """
        SELECT 
            endpoint,
            method,
            COUNT(*) as requests,
            AVG(duration_ms) as avg_duration,
            MAX(duration_ms) as max_duration,
            100.0 * SUM(CASE WHEN status_code < 400 THEN 1 ELSE 0 END) / COUNT(*) as success_rate
        FROM access_logs a
        JOIN execution_logs e ON a.request_id = e.request_id
        WHERE a.timestamp BETWEEN ? AND ?
        GROUP BY endpoint, method
        ORDER BY requests DESC
        LIMIT 20
        """
        endpoint_data = run_query(conn, query, (start_date, end_date))
        
        if not endpoint_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Top Endpoints by Volume")
                fig = create_bar_chart(
                    endpoint_data.head(10), 
                    'endpoint', 
                    'requests', 
                    'Top Endpoints by Request Count',
                    'method'
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Performance vs Success Rate")
                fig = px.scatter(
                    endpoint_data,
                    x='avg_duration',
                    y='success_rate',
                    size='requests',
                    color='endpoint',
                    hover_name='endpoint',
                    log_x=True,
                    labels={
                        'avg_duration': 'Average Duration (ms)',
                        'success_rate': 'Success Rate (%)'
                    }
                )
                fig.update_layout(
                    template="plotly_dark",
                    margin=dict(l=20, r=20, t=60, b=20),
                    font=dict(family="Segoe UI", size=12),
                    plot_bgcolor="#0E1117",
                    paper_bgcolor="#0E1117",
                    hoverlabel=dict(bgcolor="#1F2C40", font_size=12)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Detailed Endpoint Metrics")
            st.dataframe(
                endpoint_data.assign(
                    avg_duration=lambda x: x['avg_duration'].round(1).astype(str) + " ms",
                    max_duration=lambda x: x['max_duration'].round(1).astype(str) + " ms",
                    success_rate=lambda x: x['success_rate'].round(1).astype(str) + "%",
                    requests=lambda x: x['requests'].apply("{:,}".format)
                ),
                height=400,
                use_container_width=True
            )
        else:
            st.warning("⚠️ No endpoint performance data available")

def security_analysis(conn: sqlite3.Connection, start_date: str, end_date: str) -> None:
    """Analyze security-related patterns and anomalies"""
    st.header("🔒 Security Analysis")
    
    with st.expander("🛡️ Threat Detection", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Failed Authentication Attempts")
            query = """
            SELECT 
                endpoint,
                COUNT(*) as failed_attempts,
                COUNT(DISTINCT user_id) as users_affected
            FROM access_logs
            WHERE timestamp BETWEEN ? AND ?
            AND status_code = 401
            GROUP BY endpoint
            ORDER BY failed_attempts DESC
            LIMIT 10
            """
            failed_auth = run_query(conn, query, (start_date, end_date))
            
            if not failed_auth.empty:
                fig = create_bar_chart(
                    failed_auth, 
                    'endpoint', 
                    'failed_attempts', 
                    'Failed Login Attempts by Endpoint'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("🛈 No failed authentication attempts detected")
        
        with col2:
            st.subheader("VPC Rejections Analysis")
            query = """
            SELECT 
                action,
                COUNT(*) as count,
                100.0 * COUNT(*) / (SELECT COUNT(*) FROM vpc_logs WHERE timestamp BETWEEN ? AND ?) as percentage
            FROM vpc_logs
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY action
            """
            vpc_actions = run_query(conn, query, (start_date, end_date, start_date, end_date))
            
            if not vpc_actions.empty:
                fig = create_pie_chart(
                    vpc_actions,
                    'action',
                    'count',
                    'VPC Actions Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("🛈 No VPC action data available")
    
    with st.expander("🔎 Suspicious Activity Patterns", expanded=True):
        query = """
        SELECT 
            v.src_ip,
            COUNT(*) as request_count,
            SUM(CASE WHEN a.status_code >= 400 THEN 1 ELSE 0 END) as errors,
            COUNT(DISTINCT a.user_id) as users_affected,
            100.0 * SUM(CASE WHEN a.status_code >= 400 THEN 1 ELSE 0 END) / COUNT(*) as error_rate,
            GROUP_CONCAT(DISTINCT a.endpoint) as endpoints_accessed
        FROM vpc_logs v
        JOIN access_logs a ON v.request_id = a.request_id
        WHERE v.timestamp BETWEEN ? AND ?
        GROUP BY v.src_ip
        HAVING request_count > 10 AND error_rate > 20
        ORDER BY error_rate DESC
        LIMIT 20
        """
        suspicious_ips = run_query(conn, query, (start_date, end_date))
        
        if not suspicious_ips.empty:
            st.subheader("Suspicious IP Activity")
            
            tab1, tab2 = st.tabs(["Table View", "Pattern Analysis"])
            
            with tab1:
                st.dataframe(
                    suspicious_ips.assign(
                        request_count=lambda x: x['request_count'].apply("{:,}".format),
                        error_rate=lambda x: x['error_rate'].round(1).astype(str) + "%",
                        users_affected=lambda x: x['users_affected'].apply("{:,}".format)
                    ),
                    height=500,
                    use_container_width=True
                )
            
            with tab2:
                fig = px.scatter(
                    suspicious_ips,
                    x='request_count',
                    y='error_rate',
                    size='users_affected',
                    color='src_ip',
                    hover_name='src_ip',
                    hover_data=['endpoints_accessed'],
                    log_x=True,
                    labels={
                        'request_count': 'Total Requests',
                        'error_rate': 'Error Rate (%)',
                        'users_affected': 'Users Affected'
                    }
                )
                fig.update_layout(
                    template="plotly_dark",
                    margin=dict(l=20, r=20, t=60, b=20),
                    font=dict(family="Segoe UI", size=12),
                    plot_bgcolor="#0E1117",
                    paper_bgcolor="#0E1117",
                    hoverlabel=dict(bgcolor="#1F2C40", font_size=12)
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🛈 No suspicious activity patterns detected")

def user_behavior_analysis(conn: sqlite3.Connection, start_date: str, end_date: str) -> None:
    """Analyze user behavior patterns"""
    st.header("👤 User Behavior Analysis")
    
    with st.expander("📊 User Activity Patterns", expanded=True):
        query = """
        SELECT
            a.user_id,
            COUNT(DISTINCT date(a.timestamp)) as active_days,
            COUNT(*) as total_requests,
            AVG(e.duration_ms) as avg_duration,
            100.0 * SUM(CASE WHEN e.status = 'SUCCESS' THEN 1 ELSE 0 END) / COUNT(*) as success_rate
        FROM access_logs a
        JOIN execution_logs e ON a.request_id = e.request_id
        WHERE a.timestamp BETWEEN ? AND ?
        GROUP BY a.user_id
        HAVING active_days > 1 AND total_requests > 10
        ORDER BY total_requests DESC
        LIMIT 50
        """
        user_activity = run_query(conn, query, (start_date, end_date))
        
        if not user_activity.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Top Users by Activity")
                fig = create_bar_chart(
                    user_activity.head(10),
                    'user_id',
                    'total_requests',
                    'Top Users by Request Volume'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Engagement vs Success")
                fig = px.scatter(
                    user_activity,
                    x='active_days',
                    y='success_rate',
                    size='total_requests',
                    color='user_id',
                    hover_name='user_id',
                    labels={
                        'active_days': 'Active Days',
                        'success_rate': 'Success Rate (%)',
                        'total_requests': 'Total Requests'
                    }
                )
                fig.update_layout(
                    template="plotly_dark",
                    margin=dict(l=20, r=20, t=60, b=20),
                    font=dict(family="Segoe UI", size=12),
                    plot_bgcolor="#0E1117",
                    paper_bgcolor="#0E1117",
                    hoverlabel=dict(bgcolor="#1F2C40", font_size=12)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Detailed User Metrics")
            st.dataframe(
                user_activity.assign(
                    total_requests=lambda x: x['total_requests'].apply("{:,}".format),
                    avg_duration=lambda x: x['avg_duration'].round(1).astype(str) + " ms",
                    success_rate=lambda x: x['success_rate'].round(1).astype(str) + "%"
                ),
                height=500,
                use_container_width=True
            )
        else:
            st.warning("⚠️ No user behavior data available")

# ==============================================
# MAIN APPLICATION
# ==============================================
def main():
    """Main application entry point"""
    configure_theme()
    
    try:
        # Get cached database connection
        conn = get_db_connection()
        
        # Verify connection is working
        test_df = run_query(conn, "SELECT name FROM sqlite_master WHERE type='table'")
        if test_df.empty:
            st.error("❌ No tables found in database. Please verify your database setup.")
            st.stop()
        
        st.sidebar.success(f"✅ Connected to database with {len(test_df)} tables")
        
        # Get date range
        start_date, end_date = date_selector()
        
        # Add sidebar filters
        st.sidebar.header("🔍 Filters")
        show_alerts = st.sidebar.checkbox("Show Critical Alerts Only", True)
        # group_by_hour = st.sidebar.checkbox("Group Data by Hour", False)
        
        # Dashboard layout
        system_health_overview(conn, start_date, end_date)
        st.markdown("---")
        
        # Performance Analysis
        performance_analysis(conn, start_date, end_date)
        st.markdown("---")
        
        # Security Analysis
        security_analysis(conn, start_date, end_date)
        st.markdown("---")
        
        # User Behavior Analysis
        user_behavior_analysis(conn, start_date, end_date)
        
    except Exception as e:
        st.error(f"❌ Critical application error: {str(e)}")
        st.stop()

# if __name__ == "__main__":
#     main()