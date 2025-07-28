# aciaria_simulator/data_logger.py

import json
import os
from datetime import datetime
from .maintenance import MaintenanceReport

class DataLogger:
    # O __init__ agora aceita um sufixo para o nome do arquivo
    def __init__(self, file_suffix: str, base_dir: str = "data"):
        timestamp = file_suffix

        # Define os diretórios
        log_directory = os.path.join(base_dir, 'logs')
        error_log_directory = os.path.join(base_dir, 'error_logs')
        maintenance_log_directory = os.path.join(base_dir, 'maintenance_reports')

        # Garante que os diretórios existam
        os.makedirs(log_directory, exist_ok=True)
        os.makedirs(error_log_directory, exist_ok=True)
        os.makedirs(maintenance_log_directory, exist_ok=True)

        # Cria os nomes de arquivo usando o sufixo do mês
        self.log_filepath = os.path.join(log_directory, f"sim_log_{timestamp}.jsonl")
        self.error_log_filepath = os.path.join(error_log_directory, f"error_log_{timestamp}.jsonl")
        self.maintenance_log_filepath = os.path.join(maintenance_log_directory, f"maintenance_reports_{timestamp}.jsonl")

        # Abre os arquivos
        self.log_file = open(self.log_filepath, 'a', encoding='utf-8')
        self.error_log_file = open(self.error_log_filepath, 'a', encoding='utf-8')
        self.maintenance_log_file = open(self.maintenance_log_filepath, 'a', encoding='utf-8')
        print(f"Logger iniciado para o período '{timestamp}'.")

    def log_sensor_data(self, data: dict):
        json.dump(data, self.log_file)
        self.log_file.write('\n')
        if data.get('status') == 'EM_FALHA':
            json.dump(data, self.error_log_file)
            self.error_log_file.write('\n')

    def log_maintenance_report(self, report: MaintenanceReport):
        json.dump(report.to_dict(), self.maintenance_log_file)
        self.maintenance_log_file.write('\n')

    def close(self):
        self.log_file.close()
        self.error_log_file.close()
        self.maintenance_log_file.close()
        print(f"Logger para o período finalizado.")