# I want a python program which will take dataset from last 15 years of English premiere league (football) in below mentioned format. I will have two dropdowns to select team1 and team2.  Output should be three tiles of home team1 win count, draw count and away team win count. A detailed table with data selectable filter(like i shold be able to select only draw from winning team column) of head to head record for last 10 years with full time score,winning team name (green if team 1 ,red if team 2, yellow if draw), home team, away team, year.
# I need on visual with two rows of team 1 and team2 showing data from recent 10 matches between them such as if team 1 won then w with green ,if draw then d with yellow and if lost then Lwith red highlight ans vice versa for team team 2
#  Data format as below:
# Season MatchDate HomeTeam AwayTeam FullTimeHomeGoals FullTimeAwayGoals FullTimeResult HalfTimeHomeGoals HalfTimeAwayGoals HalfTimeResult HomeShots AwayShots HomeShotsOnTarget AwayShotsOnTarget HomeCorners AwayCorners HomeFouls AwayFouls HomeYellowCards AwayYellowCards HomeRedCards AwayRedCards 
# 2024/25 16-08-2024 Man United Fulham 1 0 H 0 0 D 14 10 5 2 7 8 12 10 2 3 0 0

import streamlit as st
import pandas as pd
import datetime

# Load the dataset
@st.cache_data
def load_data():
    df = pd.read_csv('epl_final.csv')
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
def main():
    st.title("English Premier League Head-to-Head Analysis")
    
    # Load data
    df = load_data()
    
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

if __name__ == "__main__":
    main()