import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import datetime
import os

### Tab 1 Player stats H2H
@st.cache_data
def load_data1():
    contents = os.listdir()
    print("Contents of Current Directory:")
    for item in contents:
        print(item)

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the CSV file
    csv_path = os.path.join(script_dir, 'epl_final.csv')

    # Read the CSV file
    df = pd.read_csv(csv_path)

    #df = pd.read_csv('epl_final.csv')
    # Convert MatchDate to datetime
    df['MatchDate'] = pd.to_datetime(df['MatchDate'], format='%d-%m-%Y')
    return df

# Function to filter head-to-head matches
def get_head_to_head(df, team1, team2, years=10):
    current_year = datetime.datetime.now().year
    start_year = current_year - years
    mask = (
        ((df['HomeTeam'] == team1) & (df['AwayTeam'] == team2)) |
        ((df['HomeTeam'] == team2) & (df['AwayTeam'] == team1))
    ) & (df['MatchDate'].dt.year >= start_year)
    return df[mask].sort_values('MatchDate', ascending=False)

# Function to calculate win/draw/loss counts
def calculate_stats(df, team1, team2):
    h2h = get_head_to_head(df, team1, team2)
    team1_wins = len(h2h[(h2h['FullTimeResult'] == 'H') & (h2h['HomeTeam'] == team1) | 
                         (h2h['FullTimeResult'] == 'A') & (h2h['AwayTeam'] == team1)])
    team2_wins = len(h2h[(h2h['FullTimeResult'] == 'H') & (h2h['HomeTeam'] == team2) | 
                         (h2h['FullTimeResult'] == 'A') & (h2h['AwayTeam'] == team2)])
    draws = len(h2h[h2h['FullTimeResult'] == 'D'])
    return team1_wins, draws, team2_wins

# Function to get recent 10 matches visualization
def get_recent_matches(df, team1, team2):
    h2h = get_head_to_head(df, team1, team2).head(10)
    team1_results = []
    team2_results = []
    
    for _, row in h2h.iterrows():
        if row['FullTimeResult'] == 'D':
            team1_results.append(('D', 'yellow'))
            team2_results.append(('D', 'yellow'))
        elif (row['FullTimeResult'] == 'H' and row['HomeTeam'] == team1) or \
             (row['FullTimeResult'] == 'A' and row['AwayTeam'] == team1):
            team1_results.append(('W', 'green'))
            team2_results.append(('L', 'red'))
        else:
            team1_results.append(('L', 'red'))
            team2_results.append(('W', 'green'))
    
    return team1_results, team2_results

# Main Streamlit app
def main1():
    st.title("English Premier League Head-to-Head Analysis")
    
    # Load data
    df = load_data1()
    
    # Team selection
    teams = sorted(set(df['HomeTeam'].unique()) | set(df['AwayTeam'].unique()))
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Select Team 1", teams, index=teams.index('Man United') if 'Man United' in teams else 0)
    with col2:
        team2 = st.selectbox("Select Team 2", teams, index=teams.index('Fulham') if 'Fulham' in teams else 1)
    
    if team1 == team2:
        st.warning("Please select different teams")
        return
    
    # Calculate statistics
    team1_wins, draws, team2_wins = calculate_stats(df, team1, team2)
    
    # Display statistics in tiles
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"{team1} Wins", team1_wins)
    with col2:
        st.metric("Draws", draws)
    with col3:
        st.metric(f"{team2} Wins", team2_wins)
    
    # Head-to-head table
    st.subheader("Head-to-Head Record (Last 10 Years)")
    h2h = get_head_to_head(df, team1, team2)
    
    # Filter for winning team
    winning_team_filter = st.selectbox("Filter by result", ["All", "Team 1 Win", "Team 2 Win", "Draw"])
    
    # Prepare table data
    table_data = h2h[['MatchDate', 'HomeTeam', 'AwayTeam', 'FullTimeHomeGoals', 'FullTimeAwayGoals', 'FullTimeResult']].copy()
    table_data['Year'] = table_data['MatchDate'].dt.year
    table_data['Score'] = table_data['FullTimeHomeGoals'].astype(str) + '-' + table_data['FullTimeAwayGoals'].astype(str)
    
    # Determine winning team and color
    table_data['Winning Team'] = table_data.apply(
        lambda row: team1 if ((row['FullTimeResult'] == 'H' and row['HomeTeam'] == team1) or 
                             (row['FullTimeResult'] == 'A' and row['AwayTeam'] == team1)) else
                    team2 if ((row['FullTimeResult'] == 'H' and row['HomeTeam'] == team2) or 
                             (row['FullTimeResult'] == 'A' and row['AwayTeam'] == team2)) else
                    'Draw', axis=1)
    
    # Apply filter
    if winning_team_filter != "All":
        if winning_team_filter == "Team 1 Win":
            table_data = table_data[table_data['Winning Team'] == team1]
        elif winning_team_filter == "Team 2 Win":
            table_data = table_data[table_data['Winning Team'] == team2]
        else:
            table_data = table_data[table_data['Winning Team'] == 'Draw']
    
    # Display table with colored winning team
    def highlight_winning_team(row):
        color = 'green' if row['Winning Team'] == team1 else 'red' if row['Winning Team'] == team2 else 'yellow'
        return [f'background-color: {color}' if col == 'Winning Team' else '' for col in row.index]
    
    styled_table = table_data[['Year', 'HomeTeam', 'AwayTeam', 'Score', 'Winning Team']].style.apply(highlight_winning_team, axis=1)
    st.dataframe(styled_table, use_container_width=True)
    
    # Recent matches visualization
    st.subheader("Last 10 Matches")
    team1_results, team2_results = get_recent_matches(df, team1, team2)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"{team1} Results")
        for result, color in team1_results:
            st.markdown(f"<span style='background-color:{color};padding:5px;color:white'>{result}</span>", unsafe_allow_html=True)
    
    with col2:
        st.write(f"{team2} Results")
        for result, color in team2_results:
            st.markdown(f"<span style='background-color:{color};padding:5px;color:white'>{result}</span>", unsafe_allow_html=True)




### Tab 2 Team stats H2H
@st.cache_data
def load_data2():
    return pd.read_csv('cleaned_Data_till_2024-25.csv')

# Main dashboard function
def main2():
    st.title("Football Team Comparison Dashboard")

    # Load data
    df = load_data2()

    # Get unique team names
    teams = sorted(df['team_x'].unique())

    # Create team selection dropdowns
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Select Team 1", teams, index=0)
    with col2:
        # Ensure Team 2 is not the same as Team 1
        team2_options = [team for team in teams if team != team1]
        team2 = st.selectbox("Select Team 2", team2_options, index=0)

    # Filter data for matches where team1 played against team2
    team1_vs_team2 = df[(df['team_x'] == team1) & (df['opp_team_name'] == team2)]
    team2_vs_team1 = df[(df['team_x'] == team2) & (df['opp_team_name'] == team1)]

    # Aggregate statistics for team1 vs team2
    team1_stats = team1_vs_team2.groupby(['name', 'position']).agg({
        'goals_scored': 'sum',
        'assists': 'sum',
        'total_points': 'sum'
    }).reset_index().sort_values(['goals_scored', 'assists'], ascending=[False, False])

    # Aggregate statistics for team2 vs team1
    team2_stats = team2_vs_team1.groupby(['name', 'position']).agg({
        'goals_scored': 'sum',
        'assists': 'sum',
        'total_points': 'sum'
    }).reset_index().sort_values(['goals_scored', 'assists'], ascending=[False, False])

    # Display tables
    st.subheader(f"{team1} Players vs {team2}")
    if not team1_stats.empty:
        st.dataframe(
            team1_stats,
            column_config={
                "name": "Player Name",
                "position": "Position",
                "goals_scored": "Total Goals",
                "assists": "Total Assists",
                "total_points": "Total Points"
            },
            hide_index=True
        )
    else:
        st.write(f"No data available for {team1} vs {team2}")

    st.subheader(f"{team2} Players vs {team1}")
    if not team2_stats.empty:
        st.dataframe(
            team2_stats,
            column_config={
                "name": "Player Name",
                "position": "Position",
                "goals_scored": "Total Goals",
                "assists": "Total Assists",
                "total_points": "Total Points"
            },
            hide_index=True
        )
    else:
        st.write(f"No data available for {team2} vs {team1}")

    # Bar charts for Team 1
    st.subheader(f"Top 5 Players for {team1} vs {team2}")
    col3, col4 = st.columns(2)

    with col3:
        # Top 5 players by goals
        top5_goals_team1 = team1_stats.nlargest(10, 'goals_scored')
        fig_goals_team1 = px.bar(
            top5_goals_team1,
            x='name',
            y='goals_scored',
            title=f"Top 5 Goal Scorers ({team1} vs {team2})",
            labels={'name': 'Player', 'goals_scored': 'Goals'},
            text='goals_scored'
        )
        fig_goals_team1.update_traces(textposition='auto')
        fig_goals_team1.update_layout(xaxis_title="Player", yaxis_title="Goals")
        st.plotly_chart(fig_goals_team1, use_container_width=True)

    with col4:
        # Top 5 players by assists
        top5_assists_team1 = team1_stats.nlargest(10, 'assists')
        fig_assists_team1 = px.bar(
            top5_assists_team1,
            x='name',
            y='assists',
            title=f"Top 5 Assist Makers ({team1} vs {team2})",
            labels={'name': 'Player', 'assists': 'Assists'},
            text='assists'
        )
        fig_assists_team1.update_traces(textposition='auto')
        fig_assists_team1.update_layout(xaxis_title="Player", yaxis_title="Assists")
        st.plotly_chart(fig_assists_team1, use_container_width=True)

    # Bar charts for Team 2
    st.subheader(f"Top 5 Players for {team2} vs {team1}")
    col5, col6 = st.columns(2)

    with col5:
        # Top 5 players by goals
        top5_goals_team2 = team2_stats.nlargest(10, 'goals_scored')
        fig_goals_team2 = px.bar(
            top5_goals_team2,
            x='name',
            y='goals_scored',
            title=f"Top 5 Goal Scorers ({team2} vs {team1})",
            labels={'name': 'Player', 'goals_scored': 'Goals'},
            text='goals_scored'
        )
        fig_goals_team2.update_traces(textposition='auto')
        fig_goals_team2.update_layout(xaxis_title="Player", yaxis_title="Goals")
        st.plotly_chart(fig_goals_team2, use_container_width=True)

    with col6:
        # Top 5 players by assists
        top5_assists_team2 = team2_stats.nlargest(10, 'assists')
        fig_assists_team2 = px.bar(
            top5_assists_team2,
            x='name',
            y='assists',
            title=f"Top 5 Assist Makers ({team2} vs {team1})",
            labels={'name': 'Player', 'assists': 'Assists'},
            text='assists'
        )
        fig_assists_team2.update_traces(textposition='auto')
        fig_assists_team2.update_layout(xaxis_title="Player", yaxis_title="Assists")
        st.plotly_chart(fig_assists_team2, use_container_width=True)





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
    tab1, tab2, tab3 = st.tabs(["Team Stat", "Player Stat", "Interactive Plot"])

    # Assign content to each tab
    with tab1:
        main1()
    
    with tab2:
        main2()
    
    with tab3:
        tab3_plot()

if __name__ == "__main__":
    main()