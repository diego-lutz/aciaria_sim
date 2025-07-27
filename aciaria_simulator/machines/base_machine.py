# aciaria_simulator/machines/base_machine.py

from abc import ABC, abstractmethod
import random
import config

class BaseMachine(ABC):
    def __init__(self, **kwargs):
        # ... (o __init__ permanece o mesmo) ...
        self.machine_id = kwargs.get('id')
        self.wear_level = kwargs.get('initial_wear', 0.0)
        self.resilience_factor = kwargs.get('resilience_factor', 1.0)
        self.base_wear_per_cycle = kwargs.get('base_wear_per_cycle', 0.0005)
        self.failure_modes = kwargs.get('failure_modes', {})
        self.status = "OCIOSA"
        self.assigned_ladle = None
        self.time_in_failure = 0
        self.active_failure_mode = None

    def _check_for_failure(self, event_multiplier: float = 1.0):
        if self.status != "EM_PRODUCAO" or not self.failure_modes:
            return
        
        # A chance de falha agora é afetada pelo multiplicador do evento global
        failure_chance = (self.wear_level ** 2) * config.FAILURE_PROBABILITY_MULTIPLIER * event_multiplier
        
        if random.random() < failure_chance:
            self.status = "EM_FALHA"
            modes = list(self.failure_modes.keys())
            weights = [mode['probability_weight'] for mode in self.failure_modes.values()]
            self.active_failure_mode = random.choices(modes, weights, k=1)[0]
            print(f"!!!!!!!! FALHA CRÍTICA (Evento Ativo: {event_multiplier > 1}) DETECTADA EM {self.machine_id} | TIPO: {self.active_failure_mode} !!!!!!!!")

    @abstractmethod
    def _run_production_step(self, time_increment_seconds: int):
        pass

    def process_step(self, time_increment_seconds: int, event_multiplier: float = 1.0):
        if self.status == "EM_PRODUCAO":
            # Passa o multiplicador para a verificação de falha
            self._check_for_failure(event_multiplier)
            if self.status == "EM_PRODUCAO":
                self._run_production_step(time_increment_seconds)
        elif self.status == "EM_FALHA" or self.status == "EM_MANUTENCAO":
            pass

    # ... (O resto do arquivo base_machine.py permanece o mesmo) ...
    @abstractmethod
    def _reset_state_for_new_cycle(self): pass
    def assign_ladle(self, ladle):
        if self.is_available():
            self.assigned_ladle = ladle
            self.status = "EM_PRODUCAO"
            self.active_failure_mode = None
            self._reset_state_for_new_cycle()
            print(f"[{self.machine_id}] Panela {ladle.ladle_id} recebida. Iniciando produção.")
            return True
        return False
    def _age(self, stress_factor: float = 1.0):
        if self.resilience_factor <= 0: self.resilience_factor = 1.0
        wear_increase = (self.base_wear_per_cycle / self.resilience_factor) * stress_factor
        self.wear_level = min(1.0, self.wear_level + wear_increase)
    def release_ladle(self, stress_factor: float = 1.0):
        self._age(stress_factor)
        released = self.assigned_ladle
        self.assigned_ladle = None
        self.status = "OCIOSA"
        print(f"[{self.machine_id}] Panela {released.ladle_id} liberada. Novo nível de desgaste: {self.wear_level:.5f}")
        return released
    def is_available(self) -> bool: return self.status == "OCIOSA"
    @abstractmethod
    def get_sensor_data(self) -> dict: pass