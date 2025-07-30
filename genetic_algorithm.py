# genetic_algorithm.py
"""
Este módulo contém o núcleo do Algoritmo Genético.
Ele é organizado para responder diretamente às perguntas sobre a implementação:
- Representação da solução (Genoma) e Inicialização
- Função de Fitness
- Seleção, Crossover e Mutação
"""
import random
import time
from config import FORMATIONS

# --- 1. Representação da Solução (Genoma) e Inicialização ---
def create_individual(roster_ids):
    """
    Método de Inicialização: Cria um único indivíduo (genoma) aleatoriamente.
    
    A representação da solução (genoma) é um dicionário Python contendo:
    - 'formation': Uma string com a formação tática (ex: "4-4-2").
    - 'lineup': Uma lista com 11 IDs únicos de jogadores.
    
    Args:
        roster_ids (list): Lista de IDs de todos os jogadores disponíveis no elenco.
        
    Returns:
        dict: Um dicionário representando um time completo (solução).
    """
    formation = random.choice(list(FORMATIONS.keys()))
    lineup = random.sample(roster_ids, 11)
    return {"formation": formation, "lineup": lineup}

# --- 2. Função de Fitness ---
def calculate_fitness(individual, roster_dict):
    """
    Função de Fitness: Avalia a qualidade de um indivíduo (solução).
    
    O objetivo é MAXIMIZAR esta função. A pontuação é calculada somando a
    "pontuação efetiva" de cada jogador, que é o seu 'overall' multiplicado
    por um fator de aptidão posicional (1.0 para posição primária, 0.9 para
    secundária, e 0.1 para improvisada).
    
    Args:
        individual (dict): O genoma a ser avaliado.
        roster_dict (dict): Dicionário para acesso rápido aos dados dos jogadores.
        
    Returns:
        float: A pontuação de fitness total do time.
    """
    def get_positional_fitness(player, required_position):
        """Função auxiliar para calcular o bônus/penalidade de posição."""
        player_positions = [pos.strip() for pos in player['player_positions'].split(',')]
        if required_position in player_positions:
            return 1.0 if required_position == player_positions[0] else 0.9
        return 0.1

    formation_name, lineup_ids = individual['formation'], individual['lineup']
    required_positions = FORMATIONS[formation_name]
    
    total_fitness = sum(
        roster_dict[pid]['overall'] * get_positional_fitness(roster_dict[pid], req_pos)
        for pid, req_pos in zip(lineup_ids, required_positions)
    )
    return total_fitness

# --- 3. Operadores Genéticos (Seleção, Crossover, Mutação) ---
def selection(population_with_fitness, elite_size):
    """
    Método de Seleção: Elitismo.
    
    Seleciona os melhores indivíduos para a próxima geração.
    - Os 'elite_size' melhores indivíduos são passados diretamente.
    - O restante da próxima geração será criado a partir de pais selecionados
      aleatoriamente deste grupo de elite.
      
    Args:
        population_with_fitness (list): Lista de tuplas (indivíduo, fitness).
        elite_size (int): O número de indivíduos da elite.
        
    Returns:
        list: A lista de pais selecionados (a elite).
    """
    # A lista já vem ordenada, então basta pegar os primeiros
    elite = [item[0] for item in population_with_fitness[:elite_size]]
    return elite

def crossover(parent1, parent2):
    """
    Método de Crossover: Híbrido.
    
    Cria um novo indivíduo (filho) a partir de dois pais.
    - Formação: Escolhida aleatoriamente entre a do pai 1 ou pai 2.
    - Escalação: Usa cruzamento de ponto único, garantindo que não haja jogadores repetidos.
    
    Args:
        parent1 (dict): O primeiro genoma pai.
        parent2 (dict): O segundo genoma pai.
        
    Returns:
        dict: O novo genoma filho.
    """
    child_formation = random.choice([parent1['formation'], parent2['formation']])
    
    crossover_point = random.randint(1, 10)
    child_lineup_part1 = parent1['lineup'][:crossover_point]
    
    # Adiciona jogadores do pai 2 que não estão na parte 1
    child_lineup_part2 = [p for p in parent2['lineup'] if p not in child_lineup_part1]
    
    child_lineup = (child_lineup_part1 + child_lineup_part2)[:11]
    
    return {"formation": child_formation, "lineup": child_lineup}

def mutation(individual, roster_ids):
    """
    Método de Mutação: Troca Simples.
    
    Aplica uma pequena alteração aleatória em um indivíduo para introduzir
    diversidade na população. Com uma probabilidade de 20%, troca um jogador
    da escalação por outro do elenco que não estava sendo usado.
    
    Args:
        individual (dict): O genoma a sofrer mutação.
        roster_ids (list): Lista de todos os jogadores disponíveis.
        
    Returns:
        dict: O genoma após a tentativa de mutação.
    """
    if random.random() < 0.2: # 20% de chance de mutar
        non_lineup_players = [pid for pid in roster_ids if pid not in individual['lineup']]
        if non_lineup_players:
            idx_to_replace = random.randint(0, 10)
            player_to_add = random.choice(non_lineup_players)
            individual['lineup'][idx_to_replace] = player_to_add
    return individual

# --- 4. Loop Evolutivo Principal ---
def run_evolution_threaded(roster, pop_size, stop_event, result_queue):
    """
    Executa o ciclo completo do Algoritmo Genético em uma thread separada.
    O critério de parada é controlado externamente pelo 'stop_event'.
    """
    roster_ids = [p['sofifa_id'] for p in roster]
    roster_dict = {p['sofifa_id']: p for p in roster}
    
    # 1. Inicialização da População
    population = [create_individual(roster_ids) for _ in range(pop_size)]
    
    generation_count = 0
    while not stop_event.is_set(): # Critério de Parada
        generation_count += 1
        
        # 2. Avaliação (Fitness)
        population_with_fitness = sorted(
            [(ind, calculate_fitness(ind, roster_dict)) for ind in population],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Envia o melhor resultado da geração para a UI
        best_ind, best_fit = population_with_fitness[0]
        avg_fit = sum(s[1] for s in population_with_fitness) / len(population_with_fitness)
        result_queue.put({
            "generation": generation_count,
            "best_fitness": best_fit,
            "avg_fitness": avg_fit,
            "formation": best_ind['formation'],
            "lineup": [roster_dict[pid] for pid in best_ind['lineup']]
        })

        # 3. Seleção
        elite_size = int(pop_size * 0.2)
        parents = selection(population_with_fitness, elite_size)
        
        # A nova geração começa com a elite
        next_generation = parents[:]
        
        # 4. Crossover e Mutação para preencher o resto da população
        while len(next_generation) < pop_size:
            p1, p2 = random.choices(parents, k=2)
            child = crossover(p1, p2)
            child = mutation(child, roster_ids)
            next_generation.append(child)
            
        population = next_generation
        time.sleep(0.05) # Pequena pausa para não sobrecarregar a CPU
