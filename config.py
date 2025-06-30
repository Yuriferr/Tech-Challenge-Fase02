# config.py

import numpy as np

# --- DADOS DOS ATIVOS ---
# Fonte: Dados históricos aproximados para fins de demonstração.
# Em um projeto real, estes dados seriam obtidos via API (ex: Yahoo Finance).

# Ativos na nossa simulação
# PETR4: Petrobras, VALE3: Vale, MGLU3: Magazine Luiza, IVVB11: S&P 500 ETF
ASSETS = ['PETR4', 'VALE3', 'MGLU3', 'IVVB11']

# Retorno médio MENSAL esperado para cada ativo
# Calculado a partir de dados históricos anuais e convertido para base mensal.
# (1 + Retorno Anual)^(1/12) - 1
MEAN_RETURNS = np.array([
    0.02,   # PETR4 ~27% ao ano
    0.015,  # VALE3 ~20% ao ano
    -0.03,  # MGLU3 (teve quedas recentes, refletindo um retorno negativo)
    0.018   # IVVB11 ~24% ao ano
])

# Matriz de covariância MENSAL entre os ativos
# Mede como os ativos se movem em relação uns aos outros.
# A diagonal principal é a variância (volatilidade^2) de cada ativo.
# Valores fora da diagonal indicam a covariância.
# Esta é uma matriz SIMPLIFICADA para o exemplo.
COV_MATRIX = np.array([
    # PETR4,  VALE3,  MGLU3,  IVVB11
    [0.010,  0.004,  0.002,  0.001],   # PETR4
    [0.004,  0.009,  0.003,  0.002],   # VALE3
    [0.002,  0.003,  0.025, -0.001],  # MGLU3
    [0.001,  0.002, -0.001,  0.006]    # IVVB11
])

# Taxa livre de risco MENSAL (ex: Selic a 10.5% ao ano)
# (1 + 0.105)^(1/12) - 1
RISK_FREE_RATE = 0.0083

# --- PARÂMETROS DO ALGORITMO GENÉTICO ---
POPULATION_SIZE = 100       # Número de carteiras em cada geração
NUM_GENERATIONS = 50        # Número de gerações para evoluir
MUTATION_RATE = 0.1         # Probabilidade de uma carteira sofrer mutação
CROSSOVER_RATE = 0.8        # Probabilidade de duas carteiras cruzarem
TOURNAMENT_SIZE = 5         # Tamanho do torneio para seleção de pais