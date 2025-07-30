# app.py
"""
Arquivo principal da aplicação.
Responsável pela criação da interface gráfica com Tkinter e por gerenciar
a comunicação entre a UI e a thread do algoritmo genético.
O critério de parada do algoritmo é controlado aqui, pelo botão 'Parar'.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from queue import Queue

# Dependências externas
from PIL import Image, ImageTk

# Módulos do projeto
from config import POSITIONS_TRANSLATED
from data_loader import load_player_data
from genetic_algorithm import run_evolution_threaded

class App(tk.Tk):
    """
    Classe principal que encapsula toda a aplicação Tkinter.
    """
    def __init__(self, player_data):
        super().__init__()
        self.player_data = player_data
        self.title("Otimizador de Time com AG (Versão Modular)")
        self.geometry("1400x800")
        
        # Variáveis de controle da thread e da UI
        self.optimization_thread = None
        self.stop_event = None
        self.result_queue = Queue()
        self.graph_data = []

        # Configuração inicial da UI
        self.setup_styles()
        self.create_layout()
        self.create_widgets()

    def setup_styles(self):
        """Configura os estilos visuais para os widgets ttk."""
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # Cores e fontes para um design mais limpo
        BG_COLOR = "#ECECEC"
        CONTROL_BG = "#E0E0E0"
        BUTTON_COLOR = "#0078D7"
        BUTTON_ACTIVE = "#005A9E"
        
        self.configure(bg=BG_COLOR)
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("Control.TFrame", background=CONTROL_BG)
        self.style.configure("TLabel", background=CONTROL_BG, font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background=CONTROL_BG, font=("Segoe UI", 16, "bold"))
        self.style.configure("Info.TLabel", background=BG_COLOR, font=("Segoe UI", 14))
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=10, borderwidth=0)
        self.style.map("TButton",
            foreground=[('disabled', 'gray'), ('!disabled', 'white')],
            background=[('disabled', '#BDBDBD'), ('active', BUTTON_ACTIVE), ('!active', BUTTON_COLOR)])
        self.style.configure("Treeview", rowheight=25, font=("Segoe UI", 9), background="#FFFFFF")
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    def create_layout(self):
        """Cria os painéis principais (frames) da aplicação."""
        self.control_frame = ttk.Frame(self, width=320, padding=15, style="Control.TFrame")
        self.control_frame.pack(side="left", fill="y", padx=(0, 5))
        self.control_frame.pack_propagate(False)

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(side="right", fill="both", expand=True)

        self.results_frame = ttk.Frame(main_frame)
        self.results_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.pitch_frame = ttk.Frame(main_frame)
        self.pitch_frame.pack(side="right", fill="both", expand=True)

    def create_widgets(self):
        """Cria e posiciona todos os widgets da aplicação em seus respectivos frames."""
        # --- Widgets de Controle ---
        ttk.Label(self.control_frame, text="Configurações", style="Title.TLabel").pack(pady=(0, 20), anchor="w")
        
        ttk.Label(self.control_frame, text="Escolha um time:").pack(anchor="w")
        teams = sorted(self.player_data['club_name'].unique())
        self.team_var = tk.StringVar(value=teams[teams.index("Paris Saint-Germain")])
        self.team_combo = ttk.Combobox(self.control_frame, textvariable=self.team_var, values=teams, state="readonly")
        self.team_combo.pack(fill="x", pady=(5, 20))
        
        ttk.Label(self.control_frame, text="Tamanho da População:").pack(anchor="w")
        self.pop_size_var = tk.IntVar(value=100)
        self.pop_slider = ttk.Scale(self.control_frame, from_=50, to=500, orient="horizontal", variable=self.pop_size_var, command=lambda v: self.pop_label.config(text=f"{int(float(v))}"))
        self.pop_slider.pack(fill="x", pady=5)
        self.pop_label = ttk.Label(self.control_frame, text="100")
        self.pop_label.pack(pady=(0, 20))

        self.start_button = ttk.Button(self.control_frame, text="Iniciar Otimização", command=self.start_optimization)
        self.start_button.pack(pady=10, ipady=5, fill="x")

        self.stop_button = ttk.Button(self.control_frame, text="Parar Otimização", command=self.stop_optimization, state="disabled")
        self.stop_button.pack(ipady=5, fill="x")
        
        # --- Widgets de Resultado ---
        self.info_label = ttk.Label(self.results_frame, text="Aguardando otimização...", style="Info.TLabel")
        self.info_label.pack(fill="x", pady=5)
        
        self.graph_canvas = tk.Canvas(self.results_frame, bg="white", height=250, bd=0, highlightthickness=0)
        self.graph_canvas.pack(fill="x", pady=10)
        
        columns = ("name", "overall", "pos", "scaled_pos")
        self.tree = ttk.Treeview(self.results_frame, columns=columns, show="headings", height=11)
        self.tree.heading("name", text="Nome"); self.tree.heading("overall", text="Overall")
        self.tree.heading("pos", text="Pos. Principal"); self.tree.heading("scaled_pos", text="Pos. Escalada")
        self.tree.column("overall", width=60, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=(10,0))
        
        # --- Widget do Campo ---
        self.field_canvas = tk.Canvas(self.pitch_frame, bg="#006400", bd=0, highlightthickness=0)
        self.field_canvas.pack(fill="both", expand=True)
        try:
            self.field_image_pil = Image.open("soccer_field.png")
        except FileNotFoundError:
            self.field_image_pil = None
        self.field_canvas.bind("<Configure>", lambda e: self.draw_pitch())

    def start_optimization(self):
        """Inicia a thread do algoritmo genético."""
        roster_df = self.player_data[self.player_data['club_name'] == self.team_var.get()]
        if len(roster_df) < 11:
            messagebox.showerror("Erro", "Elenco com menos de 11 jogadores.")
            return

        self.start_button.config(state="disabled"); self.stop_button.config(state="normal")
        self.team_combo.config(state="disabled"); self.pop_slider.config(state="disabled")

        self.graph_data = [] # Limpa dados do gráfico anterior
        
        self.stop_event = threading.Event()
        self.optimization_thread = threading.Thread(
            target=run_evolution_threaded,
            args=(roster_df.to_dict('records'), self.pop_size_var.get(), self.stop_event, self.result_queue),
            daemon=True
        )
        self.optimization_thread.start()
        self.after(100, self.process_queue)

    def stop_optimization(self):
        """Define o critério de parada, interrompendo a thread do AG."""
        if self.stop_event: self.stop_event.set()
        self.start_button.config(state="normal"); self.stop_button.config(state="disabled")
        self.team_combo.config(state="normal"); self.pop_slider.config(state="normal")

    def process_queue(self):
        """Processa os resultados da fila de forma otimizada para não travar a UI."""
        latest_result = None
        try:
            while not self.result_queue.empty():
                latest_result = self.result_queue.get_nowait()
        except Queue.Empty:
            pass

        if latest_result:
            self.update_ui_with_result(latest_result)

        if self.optimization_thread and self.optimization_thread.is_alive():
            self.after(250, self.process_queue)
        else:
            if self.stop_event and not self.stop_event.is_set():
                 self.stop_optimization()

    def update_ui_with_result(self, result):
        """Atualiza todos os componentes da UI com um novo resultado."""
        self.info_label.config(text=f"Geração: {result['generation']} | Melhor Fitness: {result['best_fitness']:.2f} | Formação: {result['formation']}")
        self.graph_data.append((result['best_fitness'], result['avg_fitness']))
        self.update_graph()
        self.update_table_and_pitch(result['formation'], result['lineup'])

    def update_graph(self):
        """Desenha o gráfico de fitness manualmente no Canvas."""
        self.graph_canvas.delete("all")
        width = self.graph_canvas.winfo_width()
        height = self.graph_canvas.winfo_height()
        
        if width <= 1 or height <= 1 or not self.graph_data: return

        padding = 20
        max_fitness = max(d[0] for d in self.graph_data) if self.graph_data else 1
        
        def scale_point(index, value):
            x = padding + (index / (len(self.graph_data) - 1 if len(self.graph_data) > 1 else 1)) * (width - 2 * padding)
            y = (height - padding) - (value / max_fitness) * (height - 2 * padding)
            return x, y

        points_best = [scale_point(i, d[0]) for i, d in enumerate(self.graph_data)]
        points_avg = [scale_point(i, d[1]) for i, d in enumerate(self.graph_data)]

        if len(points_best) > 1:
            self.graph_canvas.create_line(points_best, fill="#0078D7", width=2.5, smooth=True)
            self.graph_canvas.create_line(points_avg, fill="#5BC0DE", width=1.5, dash=(4, 4), smooth=True)
    
    def update_table_and_pitch(self, formation, lineup):
        """Atualiza a tabela de jogadores e o campo."""
        from config import FORMATIONS # Importa aqui para evitar dependência circular no topo
        for item in self.tree.get_children(): self.tree.delete(item)
        required_positions = FORMATIONS[formation]
        for i, player in enumerate(lineup):
            main_pos_pt = POSITIONS_TRANSLATED.get(player['main_position'], player['main_position'])
            req_pos_pt = POSITIONS_TRANSLATED.get(required_positions[i], required_positions[i])
            self.tree.insert("", "end", values=(player['short_name'], player['overall'], main_pos_pt, req_pos_pt))
        self.draw_pitch()

    def draw_pitch(self):
        """Desenha o campo de futebol e os jogadores."""
        self.field_canvas.delete("all")
        width = self.field_canvas.winfo_width()
        height = self.field_canvas.winfo_height()

        if width <= 1 or height <= 1: return

        if self.field_image_pil:
            try:
                img_resized = self.field_image_pil.resize((width, height), Image.LANCZOS)
                self.field_tk_image = ImageTk.PhotoImage(img_resized)
                self.field_canvas.create_image(0, 0, anchor="nw", image=self.field_tk_image)
            except Exception:
                self.field_canvas.configure(bg="#006400") # Fallback
        else:
             self.field_canvas.configure(bg="#006400")
        
        lineup_data = self.tree.get_children()
        if not lineup_data: return

        pos_map = {'GK': (50, 5), 'RB': (85, 25), 'LB': (15, 25), 'CB': (50, 25), 'RWB': (90, 40), 'LWB': (10, 40), 'CDM': (50, 40), 'CM': (50, 55), 'RM': (80, 60), 'LM': (20, 60), 'CAM': (50, 70), 'RW': (85, 80), 'LW': (15, 80), 'ST': (50, 85)}
        
        translated_to_abbr = {v: k for k, v in POSITIONS_TRANSLATED.items()}
        required_positions_abbr = [translated_to_abbr.get(self.tree.item(item_id)['values'][3]) for item_id in lineup_data]

        cb_count = required_positions_abbr.count('CB'); st_count = required_positions_abbr.count('ST'); cm_count = required_positions_abbr.count('CM')
        cb_idx, st_idx, cm_idx = 0, 0, 0
        
        for i, item_id in enumerate(lineup_data):
            player_name, _, _, pos_translated = self.tree.item(item_id)['values']
            pos_abbr = required_positions_abbr[i]
            if not pos_abbr: continue

            left_pct, top_pct = pos_map.get(pos_abbr, (0.5, 0.5))
            if pos_abbr == 'CB' and cb_count > 1: left_pct = 38 if cb_idx == 0 else 62; cb_idx += 1
            if pos_abbr == 'ST' and st_count > 1: left_pct = 40 if st_idx == 0 else 60; st_idx += 1
            if pos_abbr == 'CM' and cm_count > 1: left_pct = 35 if cm_idx == 0 else 65; cm_idx += 1
            
            x, y = left_pct * width / 100, top_pct * height / 100
            
            self.field_canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="#0078D7", outline="white", width=2)
            self.field_canvas.create_text(x, y, text=player_name, fill="white", font=("Segoe UI", 8, "bold"))

if __name__ == "__main__":
    # Ponto de entrada da aplicação
    df = load_player_data()
    if df is None:
        # Cria uma root temporária para mostrar o erro se o carregamento de dados falhar
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Erro Fatal", "O arquivo 'players_22.csv' não foi encontrado.")
    else:
        app = App(df)
        app.mainloop()