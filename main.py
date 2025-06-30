# main.py

import pygame
import numpy as np
from config import ASSETS, POPULATION_SIZE, MUTATION_RATE, CROSSOVER_RATE, TOURNAMENT_SIZE
from algoritmo_genetico import GeneticAlgorithm

# --- Configurações do Pygame ---
pygame.init()
WIDTH, HEIGHT = 1200, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de Carteira de Investimentos com AG (Contínuo)")
FONT = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 24)
FONT_TITLE = pygame.font.Font(None, 40)
CLOCK = pygame.time.Clock()

# --- Cores ---
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
COLOR_TEXT = pygame.Color('black')
COLOR_BG = pygame.Color('whitesmoke')
COLOR_RESULTS_BG = pygame.Color(230, 230, 250)
COLOR_BUTTON_START = pygame.Color('darkgreen')
COLOR_BUTTON_PAUSE = pygame.Color('darkorange')
COLOR_BUTTON_TEXT = pygame.Color('white')
COLOR_GRAPH_BG = pygame.Color('white')
COLOR_GRAPH_LINE = pygame.Color('blue')
COLOR_GRAPH_AXIS = pygame.Color('gray')

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, COLOR_TEXT)
        self.active = False
        self.enabled = True

    def handle_event(self, event):
        if not self.enabled: return
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isdigit() or (event.unicode == '.' and '.' not in self.text):
                    self.text += event.unicode
            self.txt_surface = FONT.render(self.text, True, COLOR_TEXT)

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)
        if not self.enabled:
            s = pygame.Surface((self.rect.width, self.rect.height))
            s.set_alpha(128)
            s.fill((200, 200, 200))
            screen.blit(s, (self.rect.x, self.rect.y))

def draw_text(text, font, color, surface, x, y, center=False):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_graph(screen, history, title):
    graph_x, graph_y, graph_w, graph_h = 670, 70, 500, 300
    graph_area = pygame.Rect(graph_x, graph_y, graph_w, graph_h)
    pygame.draw.rect(screen, COLOR_GRAPH_BG, graph_area)
    pygame.draw.rect(screen, COLOR_GRAPH_AXIS, graph_area, 2)
    draw_text(title, FONT, COLOR_TEXT, screen, graph_x, graph_y - 40)
    if not history: return

    max_val, min_val = max(history), min(history)
    range_val = max_val - min_val if max_val != min_val else 1.0
    
    points = []
    for i, val in enumerate(history):
        x = graph_x + (i / (len(history) - 1 if len(history) > 1 else 1)) * graph_w
        y = graph_y + graph_h - ((val - min_val) / range_val * (graph_h - 20) + 10)
        points.append((x, y))

    if len(points) > 1:
        pygame.draw.lines(screen, COLOR_GRAPH_LINE, False, points, 2)

    draw_text(f"{max_val:.4f}", FONT_SMALL, COLOR_GRAPH_AXIS, screen, graph_x + 5, graph_y + 5)
    draw_text(f"{min_val:.4f}", FONT_SMALL, COLOR_GRAPH_AXIS, screen, graph_x + 5, graph_y + graph_h - 25)

def main():
    running = True
    input_box_valor = InputBox(350, 100, 140, 32, "10000")
    input_box_meses = InputBox(350, 150, 140, 32, "120")
    input_boxes = [input_box_valor, input_box_meses]
    
    button_rect = pygame.Rect(50, 220, 250, 50)
    
    # Estados da Simulação: IDLE, RUNNING, PAUSED
    simulation_state = "IDLE"
    
    # Variáveis da Simulação
    ga = None
    best_solution_so_far = None
    generation_count = 0
    sharpe_history = []
    results_display = {}

    while running:
        # --- Loop de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for box in input_boxes:
                box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    if simulation_state == "IDLE":
                        try:
                            val = float(input_box_valor.text)
                            mes = int(input_box_meses.text)
                            if val > 0 and mes > 0:
                                # Inicia a simulação
                                ga = GeneticAlgorithm(POPULATION_SIZE, MUTATION_RATE, CROSSOVER_RATE, TOURNAMENT_SIZE)
                                best_solution_so_far = None
                                generation_count = 0
                                sharpe_history = []
                                for box in input_boxes: box.enabled = False
                                simulation_state = "RUNNING"
                        except (ValueError, IndexError):
                            print("Erro: Insira valores numéricos válidos.")
                    elif simulation_state == "RUNNING":
                        simulation_state = "PAUSED"
                    elif simulation_state == "PAUSED":
                        simulation_state = "RUNNING"

        # --- Lógica da Simulação (se estiver rodando) ---
        if simulation_state == "RUNNING":
            generation_count += 1
            best_of_gen = ga.evolve_one_generation(best_solution_so_far)
            sharpe_history.append(best_of_gen['fitness'])

            if best_solution_so_far is None or best_of_gen['fitness'] > best_solution_so_far['fitness']:
                best_solution_so_far = best_of_gen
                print(f"NOVO MELHOR! Geração: {generation_count}, Sharpe: {best_solution_so_far['fitness']:.4f}")
                
                # Prepara os resultados para exibição
                valor_inicial = float(input_box_valor.text)
                meses = int(input_box_meses.text)
                retorno_mensal = best_solution_so_far['return']
                valor_final = valor_inicial * ((1 + retorno_mensal) ** meses)
                results_display = {
                    "weights": best_solution_so_far['weights'],
                    "stats": {
                        "sharpe_ratio": best_solution_so_far['fitness'],
                        "expected_return_monthly": retorno_mensal,
                        "expected_volatility_monthly": best_solution_so_far['volatility']
                    },
                    "initial_value": valor_inicial,
                    "final_value": valor_final,
                    "months": meses
                }

        # --- Desenho na Tela ---
        SCREEN.fill(COLOR_BG)
        draw_text('Simulador de Otimização de Carteira', FONT_TITLE, COLOR_TEXT, SCREEN, 50, 20)
        draw_text('Valor Inicial (R$):', FONT, COLOR_TEXT, SCREEN, 50, 105)
        draw_text('Tempo (meses):', FONT, COLOR_TEXT, SCREEN, 50, 155)
        for box in input_boxes:
            box.draw(SCREEN)

        # Botão dinâmico
        if simulation_state == "IDLE":
            pygame.draw.rect(SCREEN, COLOR_BUTTON_START, button_rect)
            draw_text("Iniciar Otimização", FONT, COLOR_BUTTON_TEXT, SCREEN, button_rect.centerx, button_rect.centery, center=True)
        elif simulation_state == "RUNNING":
            pygame.draw.rect(SCREEN, COLOR_BUTTON_PAUSE, button_rect)
            draw_text("Pausar", FONT, COLOR_BUTTON_TEXT, SCREEN, button_rect.centerx, button_rect.centery, center=True)
        elif simulation_state == "PAUSED":
            pygame.draw.rect(SCREEN, COLOR_BUTTON_START, button_rect)
            draw_text("Continuar", FONT, COLOR_BUTTON_TEXT, SCREEN, button_rect.centerx, button_rect.centery, center=True)
        
        # Exibição de Geração
        if simulation_state != "IDLE":
            draw_text(f"Geração: {generation_count}", FONT, COLOR_TEXT, SCREEN, 350, 235)

        # Gráfico
        draw_graph(SCREEN, sharpe_history, "Evolução do Melhor Fitness por Geração")

        # Exibe os melhores resultados encontrados
        if results_display:
            res_y = 300
            res_x = 50
            pygame.draw.rect(SCREEN, COLOR_RESULTS_BG, (res_x - 20, res_y - 10, 580, 290), border_radius=15)
            draw_text("Melhor Carteira Encontrada até Agora:", FONT, COLOR_TEXT, SCREEN, res_x, res_y)
            res_y += 40
            
            # Alocação
            for i, asset in enumerate(ASSETS):
                text = f"{asset}: {results_display['weights'][i]*100:.2f}%"
                draw_text(text, FONT_SMALL, COLOR_TEXT, SCREEN, res_x, res_y)
                res_y += 25
            
            res_y += 15
            # Estatísticas
            stats = results_display['stats']
            draw_text(f"Retorno Mensal Esperado: {stats['expected_return_monthly']*100:.2f}%", FONT_SMALL, COLOR_TEXT, SCREEN, res_x, res_y)
            res_y += 25
            draw_text(f"Volatilidade Mensal Esperada: {stats['expected_volatility_monthly']*100:.2f}%", FONT_SMALL, COLOR_TEXT, SCREEN, res_x, res_y)
            res_y += 25
            draw_text(f"Índice de Sharpe: {stats['sharpe_ratio']:.4f}", FONT_SMALL, COLOR_TEXT, SCREEN, res_x, res_y)
            res_y += 35

            # Projeção
            val_ini_txt = f"R$ {results_display['initial_value']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            val_fim_txt = f"R$ {results_display['final_value']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            draw_text(f"Valor Inicial Simulado: {val_ini_txt}", FONT_SMALL, COLOR_TEXT, SCREEN, res_x, res_y)
            res_y += 25
            draw_text(f"Valor Final Estimado em {results_display['months']} meses: {val_fim_txt}", FONT, (0,100,0), SCREEN, res_x, res_y)

        pygame.display.flip()
        CLOCK.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()