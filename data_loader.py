# data_loader.py
"""
Módulo responsável pelo carregamento e pré-processamento dos dados.
Isola a lógica de manipulação de dados do resto da aplicação.
"""
import pandas as pd
import os

def load_player_data():
    """
    Carrega os dados dos jogadores do arquivo CSV 'players_22.csv'.
    - Seleciona apenas as colunas relevantes para o projeto.
    - Remove jogadores sem clube.
    - Extrai a posição principal de cada jogador para uso na avaliação.

    Retorna:
        - DataFrame do Pandas com os dados dos jogadores ou None se o arquivo não for encontrado.
    """
    file_path = 'players_22.csv'
    if not os.path.exists(file_path):
        return None
    
    df = pd.read_csv(file_path, low_memory=False)
    
    # Colunas que serão utilizadas pelo algoritmo e pela interface
    columns_to_keep = ['sofifa_id', 'short_name', 'overall', 'club_name', 'player_positions']
    df = df[columns_to_keep]
    
    # Limpeza de dados: remove jogadores sem clube (agentes livres)
    df = df.dropna(subset=['club_name'])
    
    # Engenharia de feature: cria a coluna 'main_position'
    df['main_position'] = df['player_positions'].apply(lambda x: x.split(',')[0].strip())
    
    return df
