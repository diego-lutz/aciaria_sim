# aciaria_simulator/machines/fea.py

from .base_machine import BaseMachine
import random

class FEA(BaseMachine):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._temperatura_banho = 300.0
        self._potencia_ativa = 0.0

    def _reset_state_for_new_cycle(self):
        """Reseta a temperatura do forno para o início de um novo ciclo."""
        self._temperatura_banho = 300.0
        self._potencia_ativa = 0.0

    def _run_production_step(self, time_increment_seconds: int):
        if self.status != "EM_PRODUCAO" or not self.assigned_ladle:
            self._potencia_ativa = 0
            return

        self._potencia_ativa = 75.0 + random.uniform(-5, 5)
        aumento_temp = (self._potencia_ativa / 50) * time_increment_seconds * 0.05
        self._temperatura_banho += aumento_temp
        self.assigned_ladle.temperature_c = self._temperatura_banho

        if self._temperatura_banho >= 1720:
            self.status = "PROCESSO_CONCLUIDO"

    def get_sensor_data(self) -> dict:
        return {
            "timestamp": "YYYY-MM-DDTHH:MM:SSZ", "machine_id": self.machine_id,
            "status": self.status, "wear_level": round(self.wear_level, 5),
            "assigned_ladle_id": self.assigned_ladle.ladle_id if self.assigned_ladle else None,
            "temperatura_banho_c": round(self._temperatura_banho, 2),
            "potencia_ativa_mw": round(self._potencia_ativa, 2),
            "corrente_eletrodo_a": round(self._potencia_ativa * 750 + random.uniform(-1000, 1000), 0),
            "temperatura_mancal_c": round(60 + (self._potencia_ativa * 0.2) + (self.wear_level * 20), 2)
        }