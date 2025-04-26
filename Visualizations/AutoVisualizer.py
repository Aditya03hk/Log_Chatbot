import pandas as pd
import plotly.express as px
from typing import List, Tuple
from utilities.is_relevant import is_relevant_chart_query


def to_dataframe(rows: List[Tuple], columns: List[str]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=columns)


def get_common_layout(title: str):
    return dict(
        title=dict(text=title, x=0.5, xanchor='center'),
        template="plotly_dark",  # Try "simple_white" for a light theme
        margin=dict(l=40, r=40, t=60, b=40),
        font=dict(family="Segoe UI", size=14),
        hoverlabel=dict(bgcolor="black", font_size=13, font_family="Segoe UI"),
        plot_bgcolor="#111111",
        paper_bgcolor="#111111"
    )


def plot_univariate(df: pd.DataFrame, column: str):
    title = f"Distribution of {column}" if pd.api.types.is_numeric_dtype(df[column]) else f"Frequency of {column}"
    
    if pd.api.types.is_numeric_dtype(df[column]):
        fig = px.histogram(
            df,
            x=column,
            marginal="box",
            nbins=30,
            color_discrete_sequence=['#00CC96'],
            opacity=0.85
        )
        fig.update_traces(
        selector=dict(type='box'),
        line=dict(color="white", width=2),
        fillcolor='rgba(0,204,150,0.2)',  
        marker=dict(color="white")
    )
    else:
        vc = df[column].value_counts().reset_index()
        vc.columns = [column, "count"]
        fig = px.bar(
            vc,
            x=column,
            y="count",
            labels={column: column, "count": "Count"},
            color_discrete_sequence=['#636EFA']
        )
    
    fig.update_layout(**get_common_layout(title))
    return fig


def plot_bivariate(df: pd.DataFrame, x: str, y: str):
    title = f"{y} vs {x}"
    
    if pd.api.types.is_numeric_dtype(df[x]) and pd.api.types.is_numeric_dtype(df[y]):
        fig = px.scatter(df, x=x, y=y, color_discrete_sequence=["#AB63FA"])
    elif pd.api.types.is_numeric_dtype(df[y]):
        fig = px.box(df, x=x, y=y, color_discrete_sequence=["#EF553B"])
    else:
        fig = px.histogram(df, x=x, color=y, barmode='group')

    fig.update_layout(**get_common_layout(title))
    return fig


def plot_multivariate(df: pd.DataFrame, dimensions: List[str]):
    if len(dimensions) == 3:
        fig = px.scatter_3d(
            df,
            x=dimensions[0],
            y=dimensions[1],
            z=dimensions[2],
            color=dimensions[0],
            opacity=0.7
        )
        fig.update_layout(**get_common_layout(f"3D Plot: {dimensions}"))
    elif len(dimensions) > 3:
        fig = px.parallel_coordinates(df, dimensions=dimensions, color=df[dimensions[0]])
        fig.update_layout(**get_common_layout("Parallel Coordinates Plot"))
    else:
        print("Need at least 3 columns for multivariate plot")
        return
    return fig


def auto_visualize(df: pd.DataFrame, query: str):
    if is_relevant_chart_query(query):
        figs = []
        numeric = df.select_dtypes(include='number').columns.tolist()
        
        if len(numeric) == 1:
            figs.append(plot_univariate(df, numeric[0]))
        elif len(numeric) == 2:
            figs.append(plot_bivariate(df, numeric[0], numeric[1]))
        elif len(numeric) >= 3:
            figs.append(plot_multivariate(df, numeric[:4]))  # choose first 4 numeric cols
        else:
            for col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    figs.append(plot_univariate(df, col))
                    break
        return figs
    else:
        return None
