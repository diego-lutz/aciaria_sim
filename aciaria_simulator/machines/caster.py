# aciaria_simulator/machines/caster.py

from .base_machine import BaseMachine
import random

class Caster(BaseMachine):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._velocidade_lingotamento = 0.0
        self._vazao_agua_resfriamento = 0.0

    def _reset_state_for_new_cycle(self):
        """Reseta os parâmetros de operação do lingotador."""
        self._velocidade_lingotamento = 0.0
        self._vazao_agua_resfriamento = 0.0

    def _run_production_step(self, time_increment_seconds: int):
        if self.status != "EM_PRODUCAO" or not self.assigned_ladle:
            self._velocidade_lingotamento = 0.0
            self._vazao_agua_resfriamento = 0.0
            return

        self._velocidade_lingotamento = 1.2 + random.uniform(-0.1, 0.1)
        self._vazao_agua_resfriamento = 2000 + random.uniform(-100, 100)
        queda_temp = self._velocidade_lingotamento * time_increment_seconds * 0.02
        self.assigned_ladle.temperature_c -= queda_temp

        if self.assigned_ladle.temperature_c <= 1520:
            self.status = "PROCESSO_CONCLUIDO"

    def get_sensor_data(self) -> dict:
        return {
            "timestamp": "YYYY-MM-DDTHH:MM:SSZ", "machine_id": self.machine_id,
            "status": self.status, "wear_level": round(self.wear_level, 5),
            "assigned_ladle_id": self.assigned_ladle.ladle_id if self.assigned_ladle else None,
            "temperatura_tundish_c": round(self.assigned_ladle.temperature_c - 15, 2) if self.assigned_ladle else None,
            "velocidade_lingotamento_m_min": round(self._velocidade_lingotamento, 2),
            "vazao_agua_resfriamento_m3_h": round(self._vazao_agua_resfriamento, 2),
            "nivel_aco_molde_percent": round(95 + random.uniform(-3, 3), 1) if self.status == "EM_PRODUCAO" else 0
        }