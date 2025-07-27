# aciaria_simulator/ladle.py

import uuid

class Ladle:
    def __init__(self, weight_kg: float, initial_composition: dict):
        self.ladle_id = str(uuid.uuid4())[:8]
        self.weight_kg = weight_kg
        self.chemical_composition = initial_composition
        self.temperature_c = 1550
        self.current_location = None

    def __repr__(self):
        return f"Ladle(id={self.ladle_id}, temp={self.temperature_c}°C, location={self.current_location})"