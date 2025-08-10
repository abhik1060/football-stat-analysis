import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Function for Tab 1 content
def tab1_content():
    st.header("Welcome to Tab 1")
    st.write("This tab displays static content.")
    st.markdown("""
    ### About This Tab
    - This is a simple static content tab.
    - It includes text, markdown, and a sample metric.
    """)
    st.metric(label="Sample Metric", value="100", delta="10%")
    st.image("https://via.placeholder.com/300", caption="Sample Image")

# Function for Tab 2 content (Data Table)
def tab2_data_table():
    st.header("Data Table - Tab 2")
    st.write("This tab displays a sample dataset in a table.")
    
    # Create sample data
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Emma'],
        'Age': [25, 30, 35, 40, 28],
        'Score': [85, 90, 78, 92, 88]
    }
    df = pd.DataFrame(data)
    
    st.dataframe(
        df,
        column_config={
            "Name": "Player Name",
            "Age": "Age",
            "Score": "Performance Score"
        },
        hide_index=True
    )
    st.write("This table shows a sample dataset with names, ages, and scores.")

# Function for Tab 3 content (Plot)
def tab3_plot():
    st.header("Interactive Plot - Tab 3")
    st.write("This tab generates an interactive sine wave plot.")
    
    # Generate sample data for plotting
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    df_plot = pd.DataFrame({'x': x, 'y': y})
    
    # Create Plotly figure
    fig = px.line(df_plot, x='x', y='y', title='Sine Wave Plot',
                  labels={'x': 'X-axis', 'y': 'Sine(X)'})
    fig.update_traces(line_color='#00ff00', line_width=2)
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("Use the plot controls to zoom, pan, or download the plot.")

# Main app function
def main():
    st.title("Multi-Tab Streamlit App")
    st.write("Select a tab below to view different content or functionalities.")

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Static Content", "Data Table", "Interactive Plot"])

    # Assign content to each tab
    with tab1:
        tab1_content()
    
    with tab2:
        tab2_data_table()
    
    with tab3:
        tab3_plot()

if __name__ == "__main__":
    main()