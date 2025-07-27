# aciaria_simulator/aciaria.py

import datetime
import random
from .ladle import Ladle
from .maintenance import MaintenanceReport
from .machines.fea import FEA
from .machines.lf import LF
from .machines.caster import Caster
import config

class Aciaria:
    def __init__(self, machine_setup: list, routing: dict, initial_ladle_params: dict):
        self.sim_time = datetime.datetime.now(datetime.timezone.utc)
        self.process_routing = routing
        self.initial_ladle_params = initial_ladle_params
        self.machines = {}
        self._initialize_machines(machine_setup)
        self.active_ladles = []
        self.finished_ladles = []
        self.ongoing_maintenance = {}
        self.active_global_event = None
        self.global_event_end_time = None
        self.global_event_multiplier = 1.0

    def _initialize_machines(self, machine_setup: list):
        # ... (este método não precisa de alteração) ...
        machine_classes = {'FEA': FEA, 'LF': LF, 'CASTER': Caster}
        for config_original in machine_setup:
            config_copy = config_original.copy()
            machine_type = config_copy.pop('type', None)
            machine_id = config_copy.get('id')
            if machine_type in machine_classes:
                self.machines[machine_id] = machine_classes[machine_type](**config_copy)
                print(f"Máquina {machine_id} do tipo {machine_type} criada.")
            else:
                print(f"AVISO: Máquina do tipo '{machine_type}' não implementada. Ignorando.")
                self.machines[machine_id] = None

    def _update_global_events(self):
        # ... (este método não precisa de alteração) ...
        if self.active_global_event and self.sim_time >= self.global_event_end_time:
            print(f"--- FIM DO EVENTO GLOBAL: {self.active_global_event} ---")
            self.active_global_event = None
            self.global_event_end_time = None
            self.global_event_multiplier = 1.0
        if not self.active_global_event:
            for event_name, event_params in config.GLOBAL_EVENTS.items():
                if random.random() < event_params['base_probability_per_step']:
                    self.active_global_event = event_name
                    duration_seconds = event_params['duration_steps'] * config.SIMULATION_STEP_SECONDS
                    self.global_event_end_time = self.sim_time + datetime.timedelta(seconds=duration_seconds)
                    self.global_event_multiplier = event_params['failure_chance_multiplier']
                    print(f"!!! INÍCIO DE EVENTO GLOBAL: {event_name}. Risco de falha aumentado por {duration_seconds/60:.0f} minutos!!!")
                    break

    def update(self, time_increment_seconds: int, logger):
        self.sim_time += datetime.timedelta(seconds=time_increment_seconds)
        self._update_global_events()

        for machine_id, machine in list(self.machines.items()):
            if not machine: continue

            # Lógica de Produção (vem primeiro para que a falha possa ser detectada)
            machine.process_step(time_increment_seconds, self.global_event_multiplier)

            # Lógica de Manutenção
            if machine.status == "EM_FALHA" and machine_id not in self.ongoing_maintenance:
                # --- CORREÇÃO APLICADA AQUI ---
                # 1. Tira a "fotografia" dos sensores no exato momento da falha
                sensor_data_at_failure = machine.get_sensor_data()
                sensor_data_at_failure["timestamp"] = self.sim_time.isoformat()
                # 2. Envia essa fotografia para o logger, que saberá colocá-la no log de erros
                logger.log_sensor_data(sensor_data_at_failure)
                # --------------------------------

                # Agora, o resto da lógica de manutenção continua
                failure_type = machine.active_failure_mode
                failure_details = machine.failure_modes[failure_type]
                repair_hours = failure_details['repair_time_hours']
                
                report = MaintenanceReport(
                    machine_id=machine_id, failure_time=self.sim_time,
                    failure_type=failure_type, repair_time_hours=repair_hours
                )
                logger.log_maintenance_report(report)
                
                machine.status = "EM_MANUTENCAO"
                repair_end_time = self.sim_time + datetime.timedelta(hours=repair_hours)
                self.ongoing_maintenance[machine_id] = {"end_time": repair_end_time, "report": report}
                print(f"[{machine_id}] entrou em MANUTENÇÃO. Reparo estimado para {repair_end_time.isoformat()}")

            elif machine.status == "EM_MANUTENCAO" and machine_id in self.ongoing_maintenance:
                if self.sim_time >= self.ongoing_maintenance[machine_id]["end_time"]:
                    print(f"[{machine_id}] MANUTENÇÃO CONCLUÍDA.")
                    failure_type = self.ongoing_maintenance[machine_id]['report'].failure_type
                    wear_reduction = machine.failure_modes[failure_type].get('repair_wear_reduction', 0.05)
                    machine.wear_level = max(0, machine.wear_level - wear_reduction)
                    print(f"[{machine_id}] Nível de desgaste reduzido para {machine.wear_level:.5f}.")
                    machine.status = "OCIOSA"
                    del self.ongoing_maintenance[machine_id]

            # Lógica de Fim de Ciclo
            if machine.status == "PROCESSO_CONCLUIDO":
                ladle = machine.release_ladle(stress_factor=1.0)
                machine_type_key = machine_id.split('_')[0]
                next_stage_key = self.process_routing.get(machine_type_key)
                if next_stage_key == 'FINISH':
                    if ladle in self.active_ladles: self.active_ladles.remove(ladle)
                    self.finished_ladles.append(ladle)
                else:
                    self._route_ladle_to_next_stage(ladle, next_stage_key)
        
        # Lógica de Criação de Novas Panelas
        first_stage_machine = self.machines.get('FEA_01')
        if first_stage_machine and first_stage_machine.is_available():
            new_ladle = Ladle(weight_kg=self.initial_ladle_params['weight'], initial_composition=self.initial_ladle_params['composition'])
            self.active_ladles.append(new_ladle)
            first_stage_machine.assign_ladle(new_ladle)
            new_ladle.current_location = first_stage_machine.machine_id

    def _route_ladle_to_next_stage(self, ladle: Ladle, next_machine_type: str):
        # ... (este método não precisa de alteração) ...
        found_machine = False
        for machine_id, machine in self.machines.items():
            if machine and machine_id.startswith(next_machine_type) and machine.is_available():
                machine.assign_ladle(ladle)
                ladle.current_location = machine_id
                found_machine = True
                break
        if not found_machine:
            print(f"Panela {ladle.ladle_id} aguardando máquina do tipo {next_machine_type} ficar disponível.")
            ladle.current_location = "AGUARDANDO_TRANSFERENCIA"