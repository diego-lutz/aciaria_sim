# aciaria_simulator/maintenance.py

import uuid
from datetime import datetime

class MaintenanceReport:
    """
    Representa um relatório de manutenção, servindo como "ground truth"
    para o treinamento do modelo de IA.
    """
    def __init__(self, machine_id: str, failure_time: datetime, failure_type: str, repair_time_hours: int, report_type: str = "CORRETIVA"):
        self.report_id = f"REP-{str(uuid.uuid4())[:8]}"
        self.machine_id = machine_id
        self.failure_time = failure_time
        self.failure_type = failure_type # Ex: 'FALHA_ELETRODO_A'
        self.report_type = report_type # CORRETIVA ou PREVENTIVA
        self.repair_time_hours = repair_time_hours
        self.maintenance_start_time = None
        self.maintenance_end_time = None

    def to_dict(self):
        """Converte o relatório em um dicionário para fácil logging."""
        return {
            "report_id": self.report_id,
            "machine_id": self.machine_id,
            "failure_time": self.failure_time.isoformat() if self.failure_time else None,
            "failure_type": self.failure_type,
            "report_type": self.report_type,
            "estimated_repair_time_hours": self.repair_time_hours,
            "maintenance_start_time": self.maintenance_start_time.isoformat() if self.maintenance_start_time else None,
            "maintenance_end_time": self.maintenance_end_time.isoformat() if self.maintenance_end_time else None,
        }