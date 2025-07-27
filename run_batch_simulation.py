# run_batch_simulation.py

import time
import config
from aciaria_simulator.aciaria import Aciaria
from aciaria_simulator.data_logger import DataLogger

# --- PARÂMETROS DA EXECUÇÃO BATCH ---
TOTAL_SIMULATION_HOURS = 1000  # Quantas horas de tempo simulado queremos gerar
# ------------------------------------

def main():
    print("MODO BATCH: Iniciando a geração de dados da simulação...")
    
    logger = DataLogger()

    aciaria = Aciaria(
        machine_setup=config.MACHINE_SETUP,
        routing=config.PROCESS_ROUTING,
        initial_ladle_params={
            'weight': config.LADLE_WEIGHT_KG,
            'composition': config.INITIAL_CHEMICAL_COMPOSITION
        }
    )
    
    total_steps = (TOTAL_SIMULATION_HOURS * 3600) // config.SIMULATION_STEP_SECONDS
    print(f"Total de horas a simular: {TOTAL_SIMULATION_HOURS}h. Total de passos: {total_steps}.")
    start_time = time.time()

    for step in range(total_steps):
        aciaria.update(config.SIMULATION_STEP_SECONDS, logger)

        for machine_id, machine in aciaria.machines.items():
            if machine:
                sensor_data = machine.get_sensor_data()
                sensor_data["timestamp"] = aciaria.sim_time.isoformat()
                logger.log_sensor_data(sensor_data)
        
        if (step + 1) % 1000 == 0:
            elapsed_time = time.time() - start_time
            print(f"Progresso: {step + 1}/{total_steps} passos concluídos. Tempo real decorrido: {elapsed_time:.2f}s")

    logger.close()
    end_time = time.time()
    print(f"Simulação em batch concluída com sucesso em {end_time - start_time:.2f} segundos.")


if __name__ == "__main__":
    import os
    if not os.path.exists("data/logs"):
        os.makedirs("data/logs")
    main()