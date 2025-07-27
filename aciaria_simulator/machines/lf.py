# aciaria_simulator/machines/lf.py

from .base_machine import BaseMachine
import random

class LF(BaseMachine):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._potencia_ativa = 0.0
        self._tempo_processado_total = 0

    def _reset_state_for_new_cycle(self):
        """Reseta o contador de tempo de processo."""
        self._tempo_processado_total = 0

    def _run_production_step(self, time_increment_seconds: int):
        if self.status != "EM_PRODUCAO" or not self.assigned_ladle:
            self._potencia_ativa = 0
            return

        self._tempo_processado_total += time_increment_seconds
        self._potencia_ativa = 15.0 + random.uniform(-2, 2)
        aumento_temp = (self._potencia_ativa / 10) * time_increment_seconds * 0.01
        self.assigned_ladle.temperature_c += aumento_temp

        if self._tempo_processado_total >= 25 * 60:
            self.status = "PROCESSO_CONCLUIDO"

    def get_sensor_data(self) -> dict:
        return {
            "timestamp": "YYYY-MM-DDTHH:MM:SSZ", "machine_id": self.machine_id,
            "status": self.status, "wear_level": round(self.wear_level, 5),
            "assigned_ladle_id": self.assigned_ladle.ladle_id if self.assigned_ladle else None,
            "temperatura_panela_c": round(self.assigned_ladle.temperature_c, 2) if self.assigned_ladle else None,
            "potencia_ativa_mw": round(self._potencia_ativa, 2),
            "agitacao_argon_l_min": round(300 + random.uniform(-20, 20), 1) if self.status == "EM_PRODUCAO" else 0
        }