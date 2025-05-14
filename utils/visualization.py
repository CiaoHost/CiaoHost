import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.data_processor import get_column_types

def visualize_data_overview(df):
    """
    Create an overview visualization of the dataset
    
    Args:
        df (pandas.DataFrame): The dataframe to visualize
    """
    # Get column types
    column_types = get_column_types(df)
    
    st.subheader("Data Overview Visualization")
    
    # Data completeness visualization
    st.write("Data Completeness:")
    missing_data = df.isna().sum().sort_values(ascending=False)
    missing_percent = (missing_data / len(df) * 100).round(2)
    
    missing_df = pd.DataFrame({
        'Column': missing_data.index,
        'Missing Values': missing_data.values,
        'Percentage': missing_percent.values
    })
    
    if not missing_df.empty and missing_df['Missing Values'].sum() > 0:
        fig = px.bar(
            missing_df.head(10),
            x='Column',
            y='Percentage',
            title='Top 10 Columns with Missing Values',
            labels={'Percentage': 'Missing Values (%)'},
            color='Percentage',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No missing values in the dataset")
    
    # Visualize numeric distribution if present
    if column_types['numeric']:
        st.write("Numeric Columns Distribution:")
        
        # Choose a column to visualize
        selected_numeric = st.selectbox(
            "Select a numeric column to visualize:",
            column_types['numeric']
        )
        
        # Create histogram
        fig = px.histogram(
            df,
            x=selected_numeric,
            title=f'Distribution of {selected_numeric}',
            marginal="box",
            nbins=30,
            opacity=0.7
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Visualize categorical distribution if present
    if column_types['categorical']:
        st.write("Categorical Columns Distribution:")
        
        # Choose a column to visualize
        selected_categorical = st.selectbox(
            "Select a categorical column to visualize:",
            column_types['categorical']
        )
        
        # Count frequencies
        value_counts = df[selected_categorical].value_counts().reset_index()
        value_counts.columns = [selected_categorical, 'Count']
        
        # Only show top 10 if many categories
        if len(value_counts) > 10:
            value_counts = value_counts.head(10)
            title = f'Top 10 Values in {selected_categorical}'
        else:
            title = f'Distribution of {selected_categorical}'
        
        # Create bar chart
        fig = px.bar(
            value_counts,
            x=selected_categorical,
            y='Count',
            title=title,
            color=selected_categorical
        )
        st.plotly_chart(fig, use_container_width=True)

def create_visualization(df, viz_type, config):
    """
    Create a visualization based on the type and configuration
    
    Args:
        df (pandas.DataFrame): The dataframe to visualize
        viz_type (str): Type of visualization to create
        config (dict): Configuration options for the visualization
        
    Returns:
        plotly.graph_objects.Figure: The created visualization
    """
    if viz_type == 'bar':
        fig = create_bar_chart(df, config)
    elif viz_type == 'line':
        fig = create_line_chart(df, config)
    elif viz_type == 'scatter':
        fig = create_scatter_plot(df, config)
    elif viz_type == 'pie':
        fig = create_pie_chart(df, config)
    elif viz_type == 'histogram':
        fig = create_histogram(df, config)
    elif viz_type == 'heatmap':
        fig = create_heatmap(df, config)
    elif viz_type == 'box':
        fig = create_box_plot(df, config)
    elif viz_type == 'violin':
        fig = create_violin_plot(df, config)
    elif viz_type == 'treemap':
        fig = create_treemap(df, config)
    elif viz_type == 'table':
        fig = create_table(df, config)
    else:
        raise ValueError(f"Unsupported visualization type: {viz_type}")
    
    # Apply common settings
    if 'title' in config:
        fig.update_layout(title=config['title'])
    
    return fig

def create_bar_chart(df, config):
    """Create a bar chart visualization"""
    x = config.get('x')
    y = config.get('y')
    color = config.get('color')
    orientation = config.get('orientation', 'v')
    
    if not x or not y:
        raise ValueError("Bar chart requires both x and y values")
    
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        orientation=orientation,
        barmode=config.get('barmode', 'group'),
        text=config.get('text'),
        labels=config.get('labels', {})
    )
    
    return fig

def create_line_chart(df, config):
    """Create a line chart visualization"""
    x = config.get('x')
    y = config.get('y')
    color = config.get('color')
    
    if not x or not y:
        raise ValueError("Line chart requires both x and y values")
    
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        markers=config.get('markers', False),
        line_shape=config.get('line_shape', 'linear'),
        labels=config.get('labels', {})
    )
    
    return fig

def create_scatter_plot(df, config):
    """Create a scatter plot visualization"""
    x = config.get('x')
    y = config.get('y')
    color = config.get('color')
    size = config.get('size')
    
    if not x or not y:
        raise ValueError("Scatter plot requires both x and y values")
    
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=size,
        opacity=config.get('opacity', 0.7),
        labels=config.get('labels', {})
    )
    
    return fig

def create_pie_chart(df, config):
    """Create a pie chart visualization"""
    names = config.get('names')
    values = config.get('values')
    
    if not names or not values:
        raise ValueError("Pie chart requires both names and values")
    
    fig = px.pie(
        df,
        names=names,
        values=values,
        color=config.get('color'),
        hole=config.get('hole', 0),
        labels=config.get('labels', {})
    )
    
    return fig

def create_histogram(df, config):
    """Create a histogram visualization"""
    x = config.get('x')
    
    if not x:
        raise ValueError("Histogram requires x value")
    
    fig = px.histogram(
        df,
        x=x,
        color=config.get('color'),
        nbins=config.get('nbins', 30),
        opacity=config.get('opacity', 0.7),
        marginal=config.get('marginal'),
        labels=config.get('labels', {})
    )
    
    return fig

def create_heatmap(df, config):
    """Create a heatmap visualization"""
    columns = config.get('columns', df.select_dtypes(include=np.number).columns.tolist())
    
    # Calculate correlation matrix
    corr = df[columns].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        colorscale=config.get('colorscale', 'RdBu_r'),
        zmin=config.get('zmin', -1),
        zmax=config.get('zmax', 1),
        colorbar=dict(title=config.get('colorbar_title', 'Correlation'))
    ))
    
    fig.update_layout(
        xaxis_title=config.get('xaxis_title', ''),
        yaxis_title=config.get('yaxis_title', '')
    )
    
    return fig

def create_box_plot(df, config):
    """Create a box plot visualization"""
    x = config.get('x')
    y = config.get('y')
    
    if not y:
        raise ValueError("Box plot requires y value")
    
    fig = px.box(
        df,
        x=x,
        y=y,
        color=config.get('color'),
        notched=config.get('notched', False),
        points=config.get('points', 'outliers'),
        labels=config.get('labels', {})
    )
    
    return fig

def create_violin_plot(df, config):
    """Create a violin plot visualization"""
    x = config.get('x')
    y = config.get('y')
    
    if not y:
        raise ValueError("Violin plot requires y value")
    
    fig = px.violin(
        df,
        x=x,
        y=y,
        color=config.get('color'),
        box=config.get('box', True),
        points=config.get('points', 'outliers'),
        labels=config.get('labels', {})
    )
    
    return fig

def create_treemap(df, config):
    """Create a treemap visualization"""
    path = config.get('path')
    values = config.get('values')
    
    if not path:
        raise ValueError("Treemap requires path value")
    
    fig = px.treemap(
        df,
        path=path,
        values=values,
        color=config.get('color'),
        color_continuous_scale=config.get('color_continuous_scale'),
        labels=config.get('labels', {})
    )
    
    return fig

def create_table(df, config):
    """Create a table visualization"""
    columns = config.get('columns', df.columns.tolist())
    rows = config.get('rows', df.shape[0])
    
    # Filter dataframe by columns and rows
    table_df = df[columns].head(rows)
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(table_df.columns),
            fill_color=config.get('header_color', 'lightblue'),
            align='center'
        ),
        cells=dict(
            values=[table_df[col] for col in table_df.columns],
            fill_color=config.get('cell_color', 'lavender'),
            align='left'
        )
    )])
    
    return fig

def render_chart_in_streamlit(fig, use_container_width=True):
    """
    Render a plotly chart in Streamlit
    
    Args:
        fig (plotly.graph_objects.Figure): The figure to render
        use_container_width (bool): Whether to use the full container width
    """
    st.plotly_chart(fig, use_container_width=use_container_width)

def suggest_visualizations(df):
    """
    Suggest appropriate visualizations based on the data
    
    Args:
        df (pandas.DataFrame): The dataframe to analyze
        
    Returns:
        list: List of suggested visualization types and configurations
    """
    suggestions = []
    column_types = get_column_types(df)
    
    # For numeric columns: histograms, box plots
    for col in column_types['numeric'][:3]:  # Limit to first 3
        suggestions.append({
            'type': 'histogram',
            'config': {
                'x': col,
                'title': f'Distribution of {col}',
                'nbins': 20
            },
            'description': f"Histogram showing the distribution of {col}"
        })
    
    # For categorical columns: bar charts, pie charts
    for col in column_types['categorical'][:3]:  # Limit to first 3
        value_counts = df[col].value_counts()
        if len(value_counts) <= 10:  # Only for columns with few unique values
            suggestions.append({
                'type': 'bar',
                'config': {
                    'x': col,
                    'y': None,  # Will be computed during rendering
                    'title': f'Count of {col}'
                },
                'description': f"Bar chart showing count of values in {col}"
            })
            
            if len(value_counts) <= 7:  # Pie charts work best with few categories
                suggestions.append({
                    'type': 'pie',
                    'config': {
                        'names': col,
                        'values': None,  # Will be computed during rendering
                        'title': f'Proportion of {col}'
                    },
                    'description': f"Pie chart showing proportion of values in {col}"
                })
    
    # For time series: line charts
    if column_types['datetime'] and column_types['numeric']:
        for date_col in column_types['datetime'][:1]:  # Limit to first date column
            for num_col in column_types['numeric'][:3]:  # Limit to first 3 numeric
                suggestions.append({
                    'type': 'line',
                    'config': {
                        'x': date_col,
                        'y': num_col,
                        'title': f'{num_col} over {date_col}'
                    },
                    'description': f"Line chart showing {num_col} over time ({date_col})"
                })
    
    # For correlations: scatter plots, correlation matrix
    if len(column_types['numeric']) >= 2:
        # Add correlation heatmap
        suggestions.append({
            'type': 'heatmap',
            'config': {
                'columns': column_types['numeric'],
                'title': 'Correlation Matrix'
            },
            'description': "Heatmap showing correlations between numeric variables"
        })
        
        # Add scatter plots for first few numeric columns
        for i, col1 in enumerate(column_types['numeric'][:2]):
            for col2 in column_types['numeric'][i+1:i+3]:
                suggestions.append({
                    'type': 'scatter',
                    'config': {
                        'x': col1,
                        'y': col2,
                        'title': f'Relationship between {col1} and {col2}'
                    },
                    'description': f"Scatter plot showing relationship between {col1} and {col2}"
                })
    
    return suggestions
