# run_batch_simulation.py

import time
import config
import os
from aciaria_simulator.aciaria import Aciaria
from aciaria_simulator.data_logger import DataLogger

# --- PARÂMETROS DA EXECUÇÃO BATCH ---
TOTAL_SIMULATION_YEARS = 3  # Agora definimos em anos!
# ------------------------------------

def main():
    print(f"MODO BATCH: Iniciando a geração de {TOTAL_SIMULATION_YEARS} anos de dados...")
    
    # Limpa o diretório de dados antigos para uma nova simulação longa
    for subdir in ['logs', 'error_logs', 'maintenance_reports']:
        dir_path = os.path.join('data', subdir)
        if os.path.exists(dir_path):
            for f in os.listdir(dir_path):
                os.remove(os.path.join(dir_path, f))

    # Inicia a Aciaria
    aciaria = Aciaria(
        machine_setup=config.MACHINE_SETUP,
        routing=config.PROCESS_ROUTING,
        initial_ladle_params={
            'weight': config.LADLE_WEIGHT_KG,
            'composition': config.INITIAL_CHEMICAL_COMPOSITION
        }
    )
    
    # --- LÓGICA DE GERAÇÃO MENSAL ---
    total_hours = TOTAL_SIMULATION_YEARS * 365.25 * 24
    total_steps = int(total_hours * 3600 / config.SIMULATION_STEP_SECONDS)
    
    print(f"Total de anos a simular: {TOTAL_SIMULATION_YEARS}. Total de passos: {total_steps}.")
    start_time = time.time()

    current_log_month = None
    logger = None

    for step in range(total_steps):
        # Determina o mês atual da simulação
        sim_month_str = aciaria.sim_time.strftime('%Y-%m')

        # Se o mês mudou (ou se é o primeiro passo), troca o logger
        if sim_month_str != current_log_month:
            if logger:
                logger.close() # Fecha os arquivos do mês anterior
            
            current_log_month = sim_month_str
            logger = DataLogger(file_suffix=current_log_month) # Cria novos arquivos para o novo mês

        # Avança a simulação
        aciaria.update(config.SIMULATION_STEP_SECONDS, logger)

        # Coleta e loga os dados de cada máquina
        for machine_id, machine in aciaria.machines.items():
            if machine:
                sensor_data = machine.get_sensor_data()
                sensor_data["timestamp"] = aciaria.sim_time.isoformat()
                logger.log_sensor_data(sensor_data)
        
        if (step + 1) % 10000 == 0: # Imprime o progresso com menos frequência
            progress_percent = ((step + 1) / total_steps) * 100
            print(f"Progresso: {progress_percent:.2f}% - Simulando data: {aciaria.sim_time.date()}")

    # Fecha o último logger ao final da simulação
    if logger:
        logger.close()

    end_time = time.time()
    print(f"Simulação de {TOTAL_SIMULATION_YEARS} anos concluída com sucesso em {end_time - start_time:.2f} segundos.")


if __name__ == "__main__":
    main()