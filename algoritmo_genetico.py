# algoritmo_genetico.py

import numpy as np
import random
from config import ASSETS, MEAN_RETURNS, COV_MATRIX, RISK_FREE_RATE

class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, crossover_rate, tournament_size):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.tournament_size = tournament_size
        self.num_assets = len(ASSETS)
        self.population = self._create_initial_population()

    def _create_individual(self):
        """Cria um indivíduo (carteira) com pesos aleatórios que somam 1."""
        weights = np.random.random(self.num_assets)
        return weights / np.sum(weights)

    def _create_initial_population(self):
        """Cria a população inicial de carteiras."""
        return [self._create_individual() for _ in range(self.population_size)]

    def _calculate_fitness(self, individual_weights):
        """Calcula o fitness (Índice de Sharpe) e retorna também o retorno e a volatilidade."""
        portfolio_return = np.sum(MEAN_RETURNS * individual_weights)
        portfolio_volatility = np.sqrt(np.dot(individual_weights.T, np.dot(COV_MATRIX, individual_weights)))

        if portfolio_volatility == 0:
            return 0, portfolio_return, portfolio_volatility

        sharpe_ratio = (portfolio_return - RISK_FREE_RATE) / portfolio_volatility
        return sharpe_ratio, portfolio_return, portfolio_volatility

    def _selection(self, population_with_fitness):
        """
        Seleção por torneio.
        --- CORREÇÃO APLICADA AQUI ---
        Usa a chave 'fitness' para comparação e retorna os 'weights' do vencedor.
        """
        tournament = random.sample(population_with_fitness, self.tournament_size)
        winner = max(tournament, key=lambda item: item['fitness'])
        return winner['weights']

    def _crossover(self, parent1, parent2):
        """Crossover aritmético."""
        if random.random() < self.crossover_rate:
            alpha = random.random()
            child1 = alpha * parent1 + (1 - alpha) * parent2
            child2 = (1 - alpha) * parent1 + alpha * parent2
            return child1 / np.sum(child1), child2 / np.sum(child2)
        return parent1, parent2

    def _mutate(self, individual):
        """Mutação com normalização."""
        if random.random() < self.mutation_rate:
            mutation_point = random.randint(0, self.num_assets - 1)
            individual[mutation_point] += random.uniform(-0.1, 0.1)
            individual[individual < 0] = 0
            individual /= np.sum(individual)
        return individual

    def evolve_one_generation(self, best_solution_so_far=None):
        """
        Executa um único ciclo de evolução: avaliação, seleção, crossover e mutação.
        Retorna a melhor solução encontrada nesta geração específica e suas estatísticas.
        """
        # 1. Avalia a população atual
        population_with_fitness = []
        for individual_weights in self.population:
            fitness, ret, vol = self._calculate_fitness(individual_weights)
            population_with_fitness.append({"weights": individual_weights, "fitness": fitness, "return": ret, "volatility": vol})

        # 2. Encontra o melhor indivíduo desta geração
        best_of_generation = max(population_with_fitness, key=lambda x: x['fitness'])

        # 3. Cria a próxima geração
        next_generation_weights = []
        
        # Elitismo Forte: Garante que a melhor solução de todas as tempos sobreviva
        if best_solution_so_far is not None:
            next_generation_weights.append(best_solution_so_far['weights'])

        # Preenche o resto da população
        while len(next_generation_weights) < self.population_size:
            parent1_weights = self._selection(population_with_fitness)
            parent2_weights = self._selection(population_with_fitness)
            child1_weights, child2_weights = self._crossover(parent1_weights, parent2_weights)
            next_generation_weights.append(self._mutate(child1_weights))
            if len(next_generation_weights) < self.population_size:
                next_generation_weights.append(self._mutate(child2_weights))
        
        self.population = next_generation_weights

        return best_of_generation