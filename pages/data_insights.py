import streamlit as st
import pandas as pd
import numpy as np
from utils.data_processor import get_column_types
from utils.ai_insights import (
    generate_ai_data_insights, 
    detect_anomalies, 
    identify_clusters,
    create_data_profile
)
from utils.visualization import create_visualization, render_chart_in_streamlit

st.set_page_config(
    page_title="AI Data Insights - DataInsight AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🔍 AI Data Insights")
    st.write("Get AI-powered insights and discover hidden patterns in your data")
    
    # Check if data is loaded
    if 'data' not in st.session_state or st.session_state.data is None:
        st.info("Please upload a dataset from the Home page first.")
        if st.button("Go to Home Page"):
            st.switch_page("app.py")
        return
    
    # Get the data
    df = st.session_state.data
    
    # Sidebar for selecting analysis type
    st.sidebar.title("Analysis Type")
    analysis_type = st.sidebar.radio(
        "Select Analysis",
        ["AI-Powered Insights", "Anomaly Detection", "Cluster Analysis", "Data Profiling"]
    )
    
    # Main content based on selected analysis type
    if analysis_type == "AI-Powered Insights":
        show_ai_insights(df)
    elif analysis_type == "Anomaly Detection":
        show_anomaly_detection(df)
    elif analysis_type == "Cluster Analysis":
        show_cluster_analysis(df)
    elif analysis_type == "Data Profiling":
        show_data_profiling(df)

def show_ai_insights(df):
    """Show AI insights page"""
    st.header("AI-Powered Insights")
    st.write("""
    Ask questions about your data or get automated insights powered by OpenAI.
    """)
    
    # Quick insights
    if st.button("Generate Quick Insights"):
        with st.spinner("Analyzing your data..."):
            insights = generate_ai_data_insights(df)
            st.write("### AI Analysis Results")
            st.markdown(insights)
    
    # Ask questions
    st.subheader("Ask a Question About Your Data")
    user_question = st.text_input("Your question")
    
    if user_question:
        if st.button("Get Answers"):
            with st.spinner("Analyzing your data..."):
                answer = generate_ai_data_insights(df, user_question)
                st.write("### AI Response")
                st.markdown(answer)
    
    # Show data sample for reference
    with st.expander("View Data Sample"):
        st.dataframe(df.head(10))

def show_anomaly_detection(df):
    """Show anomaly detection page"""
    st.header("Anomaly Detection")
    st.write("""
    Identify unusual patterns and outliers in your dataset that might require further investigation.
    """)
    
    # Get numeric columns
    numeric_cols = get_column_types(df)['numeric']
    
    if not numeric_cols:
        st.warning("Anomaly detection requires numeric columns in your dataset.")
        return
    
    # Configuration panel
    with st.expander("Detection Settings", expanded=True):
        # Select columns for anomaly detection
        selected_cols = st.multiselect(
            "Select columns for anomaly detection",
            numeric_cols,
            default=numeric_cols[:min(5, len(numeric_cols))]
        )
        
        # Anomaly threshold
        contamination = st.slider(
            "Expected proportion of anomalies",
            0.01, 0.2, 0.05, 0.01,
            help="Lower values mean fewer but more significant anomalies"
        )
        
        # Run detection button
        detect_button = st.button("Detect Anomalies")
    
    # Run anomaly detection if requested
    if detect_button or ('anomalies_df' in st.session_state and selected_cols):
        if detect_button or selected_cols != st.session_state.get('last_anomaly_cols'):
            with st.spinner("Detecting anomalies..."):
                anomalies_df = detect_anomalies(df, selected_cols, contamination)
                st.session_state.anomalies_df = anomalies_df
                st.session_state.last_anomaly_cols = selected_cols
        else:
            anomalies_df = st.session_state.anomalies_df
        
        if 'error' in anomalies_df.columns:
            st.error(anomalies_df['error'][0])
            return
        
        # Show results
        st.subheader("Anomaly Detection Results")
        
        # Summary of anomalies
        anomaly_count = (anomalies_df['is_anomaly'] == 'Yes').sum()
        st.metric("Detected Anomalies", f"{anomaly_count} ({(anomaly_count/len(anomalies_df)*100):.1f}%)")
        
        # Visualization of anomalies
        if len(selected_cols) >= 2:
            st.write("### Anomaly Visualization")
            
            viz_cols = st.columns(2)
            with viz_cols[0]:
                x_col = st.selectbox("X-axis", selected_cols, index=0)
            with viz_cols[1]:
                y_col = st.selectbox("Y-axis", selected_cols, index=min(1, len(selected_cols)-1))
            
            # Create scatter plot
            fig = create_visualization(
                anomalies_df,
                "scatter",
                {
                    "x": x_col,
                    "y": y_col,
                    "color": "is_anomaly",
                    "title": "Anomaly Detection Results",
                    "opacity": 0.7
                }
            )
            render_chart_in_streamlit(fig)
        
        # Show anomaly data table
        st.write("### Top Anomalies")
        
        # Show most anomalous records first
        top_anomalies = anomalies_df[anomalies_df['is_anomaly'] == 'Yes'].head(10)
        if not top_anomalies.empty:
            st.dataframe(top_anomalies[selected_cols + ['anomaly_score']])
        else:
            st.info("No anomalies detected with the current settings.")
            
        # Distribution of anomaly scores
        if not anomalies_df.empty:
            st.write("### Distribution of Anomaly Scores")
            fig = create_visualization(
                anomalies_df,
                "histogram",
                {
                    "x": "anomaly_score",
                    "color": "is_anomaly",
                    "title": "Distribution of Anomaly Scores",
                    "nbins": 30
                }
            )
            render_chart_in_streamlit(fig)

def show_cluster_analysis(df):
    """Show cluster analysis page"""
    st.header("Cluster Analysis")
    st.write("""
    Discover natural groupings in your data to identify segments and patterns.
    """)
    
    # Get numeric columns
    numeric_cols = get_column_types(df)['numeric']
    
    if not numeric_cols:
        st.warning("Cluster analysis requires numeric columns in your dataset.")
        return
    
    # Configuration panel
    with st.expander("Clustering Settings", expanded=True):
        # Select columns for clustering
        selected_cols = st.multiselect(
            "Select columns for clustering analysis",
            numeric_cols,
            default=numeric_cols[:min(5, len(numeric_cols))]
        )
        
        # Number of clusters
        n_clusters = st.slider("Number of clusters", 2, 10, 3)
        
        # Run clustering button
        cluster_button = st.button("Identify Clusters")
    
    # Run cluster analysis if requested
    if cluster_button or ('clustered_df' in st.session_state and selected_cols):
        if cluster_button or selected_cols != st.session_state.get('last_cluster_cols') or n_clusters != st.session_state.get('last_n_clusters'):
            with st.spinner("Identifying clusters..."):
                clustered_df, centers = identify_clusters(df, selected_cols, n_clusters)
                st.session_state.clustered_df = clustered_df
                st.session_state.cluster_centers = centers
                st.session_state.last_cluster_cols = selected_cols
                st.session_state.last_n_clusters = n_clusters
        else:
            clustered_df = st.session_state.clustered_df
            centers = st.session_state.cluster_centers
        
        if 'error' in clustered_df.columns:
            st.error(clustered_df['error'][0])
            return
        
        # Show results
        st.subheader("Cluster Analysis Results")
        
        # Cluster distribution
        cluster_counts = clustered_df['cluster'].value_counts().sort_index()
        
        st.write("### Cluster Distribution")
        fig = create_visualization(
            pd.DataFrame({
                'Cluster': cluster_counts.index,
                'Count': cluster_counts.values
            }),
            "bar",
            {
                "x": "Cluster",
                "y": "Count",
                "title": "Records per Cluster",
                "color": "Cluster"
            }
        )
        render_chart_in_streamlit(fig)
        
        # Visualization of clusters
        if len(selected_cols) >= 2:
            st.write("### Cluster Visualization")
            
            viz_cols = st.columns(2)
            with viz_cols[0]:
                x_col = st.selectbox("X-axis", selected_cols, index=0)
            with viz_cols[1]:
                y_col = st.selectbox("Y-axis", selected_cols, index=min(1, len(selected_cols)-1))
            
            # Create scatter plot
            fig = create_visualization(
                clustered_df,
                "scatter",
                {
                    "x": x_col,
                    "y": y_col,
                    "color": "cluster",
                    "title": f"Clusters by {x_col} and {y_col}",
                    "opacity": 0.7
                }
            )
            render_chart_in_streamlit(fig)
        
        # Show cluster centers
        if centers is not None:
            st.write("### Cluster Centers")
            st.dataframe(centers)
            
            # Radar chart of cluster centers
            if len(selected_cols) >= 3:
                st.write("### Cluster Profiles")
                
                # Normalize cluster centers for radar chart
                radar_data = []
                
                # Get min/max values for normalization
                mins = df[selected_cols].min()
                maxs = df[selected_cols].max()
                
                # For each cluster center, create normalized values
                for i in range(n_clusters):
                    center = centers[centers['cluster'] == i].iloc[0]
                    
                    radar_data.append({
                        'Cluster': f"Cluster {i}",
                    })
                    
                    # Add normalized values (0-1 scale)
                    for col in selected_cols:
                        if maxs[col] > mins[col]:  # Avoid division by zero
                            norm_val = (center[col] - mins[col]) / (maxs[col] - mins[col])
                            radar_data[-1][col] = norm_val
                        else:
                            radar_data[-1][col] = 0.5  # Default if all values are the same
                
                radar_df = pd.DataFrame(radar_data)
                
                # Create radar chart using scatterpolar
                import plotly.graph_objects as go
                
                fig = go.Figure()
                for i in range(n_clusters):
                    row = radar_df[radar_df['Cluster'] == f"Cluster {i}"].iloc[0]
                    values = [row[col] for col in selected_cols]
                    values.append(values[0])  # Close the loop
                    theta = selected_cols + [selected_cols[0]]  # Close the loop
                    
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=theta,
                        fill='toself',
                        name=f'Cluster {i}'
                    ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )
                    ),
                    title="Normalized Cluster Profiles",
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Show sample data from each cluster
        st.write("### Sample Records from Each Cluster")
        
        for i in range(n_clusters):
            with st.expander(f"Cluster {i} Samples"):
                cluster_sample = clustered_df[clustered_df['cluster'] == i].head(5)
                if not cluster_sample.empty:
                    st.dataframe(cluster_sample[selected_cols])
                else:
                    st.info(f"No records in Cluster {i}")

def show_data_profiling(df):
    """Show data profiling page"""
    st.header("Data Profiling")
    st.write("""
    Get a comprehensive overview of your dataset's characteristics, quality, and structure.
    """)
    
    # Create data profile
    with st.spinner("Generating data profile..."):
        profile = create_data_profile(df)
    
    # Show basic information
    st.subheader("Dataset Overview")
    
    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", f"{profile['basic_info']['rows']:,}")
    with col2:
        st.metric("Columns", profile['basic_info']['columns'])
    with col3:
        st.metric("Memory Usage", f"{profile['basic_info']['memory_usage']:.2f} MB")
    with col4:
        st.metric("Duplicate Rows", f"{profile['basic_info']['duplicate_rows']:,}")
    
    # Missing values overview
    st.subheader("Data Completeness")
    
    if profile['missing_values']:
        missing_data = []
        for col, info in profile['missing_values'].items():
            missing_data.append({
                'Column': col,
                'Missing Count': info['count'],
                'Missing Percentage': info['percent']
            })
        
        missing_df = pd.DataFrame(missing_data)
        
        # Create a bar chart of missing values
        fig = create_visualization(
            missing_df,
            "bar",
            {
                "x": "Column",
                "y": "Missing Percentage",
                "title": "Missing Values by Column",
                "color": "Missing Percentage",
                "color_continuous_scale": "Reds"
            }
        )
        render_chart_in_streamlit(fig)
    else:
        st.success("No missing values found in the dataset!")
    
    # Column information
    st.subheader("Column Information")
    
    # Group columns by type
    column_tabs = st.tabs(["All Columns", "Numeric", "Categorical", "DateTime", "Text"])
    
    with column_tabs[0]:
        st.dataframe(pd.DataFrame(profile['column_info']))
    
    with column_tabs[1]:
        numeric_info = [col for col in profile['column_info'] if 'mean' in col]
        if numeric_info:
            st.dataframe(pd.DataFrame(numeric_info))
        else:
            st.info("No numeric columns in the dataset.")
    
    with column_tabs[2]:
        categorical_info = [col for col in profile['column_info'] if 'most_common' in col]
        if categorical_info:
            st.dataframe(pd.DataFrame(categorical_info))
        else:
            st.info("No categorical columns in the dataset.")
    
    with column_tabs[3]:
        datetime_info = [col for col in profile['column_info'] if 'datetime' in col['type']]
        if datetime_info:
            st.dataframe(pd.DataFrame(datetime_info))
        else:
            st.info("No datetime columns in the dataset.")
    
    with column_tabs[4]:
        text_info = [col for col in profile['column_info'] 
                     if col['type'] in ('object', 'string') and col['unique_values'] > 10]
        if text_info:
            st.dataframe(pd.DataFrame(text_info))
        else:
            st.info("No text columns in the dataset.")
    
    # Correlations
    if profile['correlations']:
        st.subheader("Correlations Between Variables")
        
        # Create a dataframe of correlations
        corr_df = pd.DataFrame(profile['correlations'])
        
        # Sort by absolute correlation
        corr_df = corr_df.sort_values(by='correlation', key=abs, ascending=False)
        
        # Create a bar chart of correlations
        fig = create_visualization(
            corr_df.head(10),
            "bar",
            {
                "x": "correlation",
                "y": [f"{row['column1']} & {row['column2']}" for _, row in corr_df.head(10).iterrows()],
                "title": "Top 10 Variable Correlations",
                "orientation": "h",
                "color": "correlation",
                "color_continuous_scale": "RdBu_r",
                "color_continuous_midpoint": 0
            }
        )
        render_chart_in_streamlit(fig)
        
        # Full correlation table
        with st.expander("View All Correlations"):
            st.dataframe(corr_df)
    
    # Data quality score
    st.subheader("Data Quality Assessment")
    
    # Calculate completeness score
    total_cells = profile['basic_info']['rows'] * profile['basic_info']['columns']
    missing_cells = sum(info['count'] for info in profile['missing_values'].values()) if profile['missing_values'] else 0
    completeness_score = 100 - (missing_cells / total_cells * 100)
    
    # Calculate consistency score (based on duplicate rows)
    consistency_score = 100 - (profile['basic_info']['duplicate_rows'] / profile['basic_info']['rows'] * 100)
    
    # Calculate average quality score
    quality_score = (completeness_score + consistency_score) / 2
    
    # Display quality scores
    quality_col1, quality_col2, quality_col3 = st.columns(3)
    
    with quality_col1:
        st.metric("Completeness Score", f"{completeness_score:.1f}%")
    with quality_col2:
        st.metric("Consistency Score", f"{consistency_score:.1f}%")
    with quality_col3:
        st.metric("Overall Quality Score", f"{quality_score:.1f}%")
    
    # Data quality recommendations
    st.subheader("Recommendations")
    
    recommendations = []
    
    # Missing values recommendations
    if profile['missing_values']:
        high_missing = [col for col, info in profile['missing_values'].items() if info['percent'] > 20]
        if high_missing:
            recommendations.append(
                f"Consider handling missing values in columns with high missing rates: {', '.join(high_missing)}"
            )
    
    # Duplicate rows recommendations
    if profile['basic_info']['duplicate_rows'] > 0:
        recommendations.append(
            f"Dataset contains {profile['basic_info']['duplicate_rows']} duplicate rows. Consider removing duplicates."
        )
    
    # Categorical columns with high cardinality
    high_cardinality = [col['name'] for col in profile['column_info'] 
                         if 'most_common' not in col and col['unique_values'] > 100]
    if high_cardinality:
        recommendations.append(
            f"Columns with high cardinality that might need grouping: {', '.join(high_cardinality)}"
        )
    
    # Display recommendations
    if recommendations:
        for i, rec in enumerate(recommendations):
            st.write(f"{i+1}. {rec}")
    else:
        st.success("No specific data quality issues detected!")

if __name__ == "__main__":
    main()
