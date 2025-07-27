# aciaria_simulator/data_logger.py

import json
import os
from datetime import datetime
from .maintenance import MaintenanceReport # Importa a classe do relatório

class DataLogger:
    def __init__(self, log_directory: str = "data/logs", error_log_directory: str = "data/error_logs", maintenance_log_directory: str = "data/maintenance_reports"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Log Principal de Sensores
        os.makedirs(log_directory, exist_ok=True)
        self.log_filepath = os.path.join(log_directory, f"sim_log_{timestamp}.jsonl")
        self.log_file = open(self.log_filepath, 'a', encoding='utf-8')
        print(f"Logger principal iniciado. Dados de sensores salvos em: {self.log_filepath}")

        # Log de Erros (Cópia dos dados de sensores durante a falha)
        os.makedirs(error_log_directory, exist_ok=True)
        self.error_log_filepath = os.path.join(error_log_directory, f"error_log_{timestamp}.jsonl")
        self.error_log_file = open(self.error_log_filepath, 'a', encoding='utf-8')
        print(f"Logger de erros iniciado. Falhas serão copiadas para: {self.error_log_filepath}")
        
        # NOVO: Log de Relatórios de Manutenção
        os.makedirs(maintenance_log_directory, exist_ok=True)
        self.maintenance_log_filepath = os.path.join(maintenance_log_directory, f"maintenance_reports_{timestamp}.jsonl")
        self.maintenance_log_file = open(self.maintenance_log_filepath, 'a', encoding='utf-8')
        print(f"Logger de manutenção iniciado. Relatórios salvos em: {self.maintenance_log_filepath}")

    def log_sensor_data(self, data: dict):
        """Escreve dados de sensores no log principal e, se for erro, no log de erros."""
        json.dump(data, self.log_file)
        self.log_file.write('\n')

        if data.get('status') == 'EM_FALHA':
            json.dump(data, self.error_log_file)
            self.error_log_file.write('\n')

    def log_maintenance_report(self, report: MaintenanceReport):
        """Escreve um relatório de manutenção no seu arquivo dedicado."""
        json.dump(report.to_dict(), self.maintenance_log_file)
        self.maintenance_log_file.write('\n')

    def close(self):
        """Fecha todos os arquivos de log de forma segura."""
        self.log_file.close()
        self.error_log_file.close()
        self.maintenance_log_file.close()
        
        print(f"Logger principal finalizado.")
        print(f"Logger de erros finalizado.")
        print(f"Logger de manutenção finalizado.")