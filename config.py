# config.py
"""
Este arquivo armazena as configurações e constantes do projeto,
definindo o "universo" do problema de otimização.
"""

# Dicionário para traduzir as abreviações de posições para português brasileiro.
# Usado para exibir os resultados de forma amigável na interface.
POSITIONS_TRANSLATED = {
    "GK": "Goleiro", "RB": "Lateral Direito", "LB": "Lateral Esquerdo", "CB": "Zagueiro",
    "RWB": "Ala Direito", "LWB": "Ala Esquerdo", "CDM": "Volante", "CM": "Meia Central",
    "RM": "Meia Direita", "LM": "Meia Esquerda", "CAM": "Meia Atacante", "RW": "Ponta Direita",
    "LW": "Ponta Esquerda", "ST": "Atacante", "CF": "Centroavante"
}

# Definição das formações táticas e as posições necessárias para cada uma.
# Esta estrutura é fundamental para a função de fitness avaliar os jogadores.
FORMATIONS = {
    "4-3-3": ["GK", "RB", "CB", "CB", "LB", "CM", "CM", "CAM", "RW", "ST", "LW"],
    "4-4-2": ["GK", "RB", "CB", "CB", "LB", "RM", "CM", "CM", "LM", "ST", "ST"],
    "3-5-2": ["GK", "CB", "CB", "CB", "RWB", "LWB", "CM", "CM", "CAM", "ST", "ST"],
    "4-2-3-1": ["GK", "RB", "CB", "CB", "LB", "CDM", "CDM", "CAM", "CAM", "CAM", "ST"]
}