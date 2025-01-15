import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime



st.set_page_config(page_title="CS2 Faceit Stats", layout="wide")

API_KEY = "api key"
BASE_URL = "https://open.faceit.com/data/v4"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "accept": "application/json"
}



def get_player_matches(player_id, limit=20):
    """Получение последних матчей игрока"""
    url = f"{BASE_URL}/players/{player_id}/history?game=cs2&offset=0&limit={limit}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None



def get_player_info(nickname):
    """Получение информации об игроке по никнейму"""
    print(nickname)
    url = f"{BASE_URL}/players?nickname={nickname}"
    response = requests.get(url, headers=HEADERS)
    print(response.json())
    if response.status_code == 200:
        return response.json()
    return None

def get_player_stats(player_id):
    """Получение статистики игрока по ID"""
    url = f"{BASE_URL}/players/{player_id}/stats/cs2"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

st.title("CS2 Faceit Statistics")

nickname = st.text_input("Введите никнейм игрока Faceit:")

if nickname:
    player_info = get_player_info(nickname)
    
    if player_info:
        st.header(f"Профиль: {player_info['nickname']}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if 'avatar' in player_info:
                st.image(player_info['avatar'], width=200)
            st.metric("Уровень Faceit", player_info['games']['cs2']['skill_level'])
            st.metric("ELO", player_info['games']['cs2']['faceit_elo'])

        stats = get_player_stats(player_info['player_id'])
        
        if stats and 'lifetime' in stats:
            lifetime = stats['lifetime']
            
            with col2:
                st.subheader("Детальная статистика")
                metrics_col1, metrics_col2 = st.columns(2)
                
                with metrics_col1:
                    st.metric("Всего матчей", lifetime['Matches'])
                    st.metric("Win Rate", f"{lifetime['Win Rate %']}%")
                    st.metric("K/D Ratio", lifetime['Average K/D Ratio'])
                
                with metrics_col2:
                    st.metric("Headshot %", f"{lifetime['Average Headshots %']}%")
                    

            with col3:
                st.subheader("Последние результаты")
                matches = get_player_matches(player_info['player_id'], 5)
                if matches:
                    last_info = ''
                    for match in matches['items']:
                        winner_team = match['results']['winner']
                        player_nick = player_info['nickname']
                        result = "❌"
                        for player in match['teams'][winner_team]['players']:
                            if player['nickname'] == player_nick:
                                result = "🏆"
                        last_info += result + ' '
                    st.write(f"{last_info}")
            
            if 'segments' in stats:
                st.subheader("Статистика по картам")
                maps_data = []
                for map_stat in stats['segments']:
                    maps_data.append({
                        'Карта': map_stat['label'],
                        'Матчи': int(map_stat['stats']['Matches']),
                        'Win Rate': float(map_stat['stats']['Win Rate %']),
                        'K/D': float(map_stat['stats']['Average K/D Ratio'])
                    })
                
                df_maps = pd.DataFrame(maps_data)
                fig_maps = px.bar(df_maps, x='Карта', y=['Win Rate', 'K/D'],
                                barmode='group',
                                title='Статистика по картам')
                st.plotly_chart(fig_maps)

    else:
        st.error("Игрок не найден")