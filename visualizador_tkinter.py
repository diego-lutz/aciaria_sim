# visualizador_comparativo_tkinter.py

import tkinter as tk
from tkinter import ttk
import pandas as pd
import os
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analisador Comparativo de Ciclos (Com Falha vs. Sem Falha)")
        self.geometry("1700x950")

        self.df_sensors = None
        self.df_maintenance = None

        # --- Frame de Controles ---
        control_frame = ttk.Frame(self)
        control_frame.pack(side="top", fill="x", padx=10, pady=10)

        ttk.Label(control_frame, text="Simulação:").pack(side="left", padx=(0, 5))
        self.sim_selector = ttk.Combobox(control_frame, state="readonly", width=30)
        self.sim_selector.pack(side="left", padx=5)
        self.sim_selector.bind("<<ComboboxSelected>>", self._load_simulation_data)

        # --- NOVO: Seletores Inteligentes ---
        ttk.Label(control_frame, text="Ciclo COM Falha:").pack(side="left", padx=(10, 5))
        self.ladle_selector_failed = ttk.Combobox(control_frame, state="disabled", width=15)
        self.ladle_selector_failed.pack(side="left", padx=5)

        ttk.Label(control_frame, text="Ciclo SEM Falha:").pack(side="left", padx=(10, 5))
        self.ladle_selector_perfect = ttk.Combobox(control_frame, state="disabled", width=15)
        self.ladle_selector_perfect.pack(side="left", padx=5)

        analyze_button = ttk.Button(control_frame, text="Comparar Ciclos", command=self._analyze_cycles)
        analyze_button.pack(side="left", padx=10)
        
        # --- Frame de Gráficos ---
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.pack(side="bottom", fill="both", expand=True, padx=10, pady=(0,5))
        
        self.fig = Figure(figsize=(16, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        
        # --- NOVO: Barra de Status para Leitura de Dados ---
        self.status_bar = ttk.Label(self, text="Mova o mouse sobre um gráfico para ver os dados", anchor="w")
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=(0, 5))
        
        # Conecta o evento de movimento do mouse à nossa função
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)

        self._find_simulations()

    def _find_simulations(self):
        log_dir = 'data/logs'
        try:
            log_files = [f for f in os.listdir(log_dir) if f.startswith('sim_log_') and f.endswith('.jsonl')]
            timestamps = sorted([f.replace('sim_log_', '').replace('.jsonl', '') for f in log_files], reverse=True)
            if timestamps:
                self.sim_selector['values'] = timestamps
                self.sim_selector.current(0)
                self._load_simulation_data(None)
        except FileNotFoundError:
            self.ladle_selector_failed.set("Pasta 'data/logs' não encontrada!")

    def _load_simulation_data(self, event):
        timestamp = self.sim_selector.get()
        # ... (código de carregamento de dados permanece o mesmo) ...
        sim_log_path = os.path.join('data', 'logs', f"sim_log_{timestamp}.jsonl")
        maintenance_log_path = os.path.join('data', 'maintenance_reports', f"maintenance_reports_{timestamp}.jsonl")
        try:
            with open(sim_log_path, 'r', encoding='utf-8') as f: self.df_sensors = pd.DataFrame([json.loads(line) for line in f if line.strip()])
            self.df_sensors['timestamp'] = pd.to_datetime(self.df_sensors['timestamp'])
            self.df_sensors['assigned_ladle_id'] = self.df_sensors['assigned_ladle_id'].astype(str)
        except Exception: self.df_sensors = pd.DataFrame()
        try:
            with open(maintenance_log_path, 'r', encoding='utf-8') as f: self.df_maintenance = pd.DataFrame([json.loads(line) for line in f if line.strip()])
            if not self.df_maintenance.empty: self.df_maintenance['failure_time'] = pd.to_datetime(self.df_maintenance['failure_time'])
        except FileNotFoundError: self.df_maintenance = pd.DataFrame()
        
        # --- NOVO: Lógica para separar ciclos com e sem falha ---
        if not self.df_sensors.empty:
            all_ladles = set(self.df_sensors['assigned_ladle_id'][self.df_sensors['assigned_ladle_id'] != 'nan'].unique())
            
            failed_ladles = set()
            if not self.df_maintenance.empty:
                for _, report in self.df_maintenance.iterrows():
                    # Encontra qual panela estava na máquina no momento da falha
                    mask = (self.df_sensors['machine_id'] == report['machine_id']) & \
                           (self.df_sensors['timestamp'] < report['failure_time'])
                    recent_logs = self.df_sensors[mask].tail(1)
                    if not recent_logs.empty:
                        failed_ladles.add(recent_logs['assigned_ladle_id'].iloc[0])

            perfect_ladles = all_ladles - failed_ladles

            # Popula os seletores
            self.ladle_selector_failed['values'] = sorted(list(failed_ladles))
            self.ladle_selector_perfect['values'] = sorted(list(perfect_ladles))
            self.ladle_selector_failed.config(state="readonly")
            self.ladle_selector_perfect.config(state="readonly")

            if failed_ladles: self.ladle_selector_failed.current(0)
            if perfect_ladles: self.ladle_selector_perfect.current(0)

    def _analyze_cycles(self):
        # ... (este método não muda, mas usa os novos seletores) ...
        ladle_failed = self.ladle_selector_failed.get()
        ladle_perfect = self.ladle_selector_perfect.get()
        if not ladle_failed or not ladle_perfect or self.df_sensors is None: return
        df_cycle_failed = self.df_sensors[self.df_sensors['assigned_ladle_id'] == ladle_failed].copy()
        df_cycle_perfect = self.df_sensors[self.df_sensors['assigned_ladle_id'] == ladle_perfect].copy()
        self._plot_comparison(df_cycle_failed, df_cycle_perfect, ladle_failed, ladle_perfect)

    def _plot_comparison(self, df_failed, df_perfect, id_failed, id_perfect):
        self.fig.clear()
        subfigs = self.fig.subfigures(1, 2, wspace=0.07)
        self._plot_single_cycle(subfigs[0], df_failed, id_failed, "Ciclo COM Falha")
        self._plot_single_cycle(subfigs[1], df_perfect, id_perfect, "Ciclo SEM Falha")
        self.canvas.draw()
    
    def _plot_single_cycle(self, subfig, df_cycle, ladle_id, title):
        # ... (Este método não muda) ...
        subfig.suptitle(f"{title}: {ladle_id}", fontsize=14)
        machines_in_cycle = sorted(df_cycle['machine_id'].unique())
        num_machines = len(machines_in_cycle)
        if num_machines == 0: return
        axes = subfig.subplots(num_machines, 1, sharex=True)
        if num_machines == 1: axes = [axes]
        sensors_map = {'FEA': ['temperatura_banho_c', 'potencia_ativa_mw'], 'LF': ['temperatura_panela_c', 'potencia_ativa_mw'], 'CASTER': ['temperatura_tundish_c', 'velocidade_lingotamento_m_min']}
        for i, machine_id in enumerate(machines_in_cycle):
            ax = axes[i]
            df_machine = df_cycle[df_cycle['machine_id'] == machine_id]
            machine_type = machine_id.split('_')[0]
            sensors = sensors_map.get(machine_type, [])
            ax.set_ylabel(machine_id, fontsize=10, rotation=0, ha='right', va='center')
            for sensor in sensors:
                if sensor in df_machine.columns: ax.plot(df_machine['timestamp'], df_machine[sensor], label=sensor)
            if not self.df_maintenance.empty:
                failures = self.df_maintenance[(self.df_maintenance['machine_id'] == machine_id) & (self.df_maintenance['failure_time'] >= df_machine['timestamp'].min()) & (self.df_maintenance['failure_time'] <= df_machine['timestamp'].max())]
                for _, report in failures.iterrows():
                    ax.axvline(x=report['failure_time'], color='red', linestyle='--', linewidth=1.5)
                    ax.text(report['failure_time'], ax.get_ylim()[1]*0.9, "FALHA", color='red', ha='center', backgroundcolor=(1,1,1,0.5))
            ax.legend(fontsize='small')
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M\n%b %d'))

    def _on_mouse_move(self, event):
        """NOVO: Função chamada toda vez que o mouse se move sobre o gráfico."""
        # Se o mouse não estiver dentro de nenhum subplot, limpa a barra de status
        if not event.inaxes:
            self.status_bar.config(text="Mova o mouse sobre um gráfico para ver os dados")
            return
        
        # Pega o subplot (ax) em que o mouse está
        ax = event.inaxes
        # Converte as coordenadas de pixel do mouse para as coordenadas de dados do gráfico
        x_data = mdates.num2date(event.xdata).strftime('%Y-%m-%d %H:%M:%S')
        y_data = event.ydata
        
        # Atualiza o texto da barra de status com as informações precisas
        machine_id = ax.get_ylabel()
        self.status_bar.config(text=f"Máquina: {machine_id}  |  Tempo: {x_data}  |  Valor: {y_data:.2f}")
        
if __name__ == "__main__":
    app = App()
    app.mainloop()