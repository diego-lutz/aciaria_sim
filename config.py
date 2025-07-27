# config.py

# PARÂMETROS GERAIS DA SIMULAÇÃO
SIMULATION_STEP_SECONDS = 5

# CONFIGURAÇÃO DA ACIARIA
PROCESS_ROUTING = {
    'FEA': 'LF',
    'LF': 'CASTER',
    'CASTER': 'FINISH'
}

# PARÂMETROS DAS MÁQUINAS
MACHINE_SETUP = [
    {
        'type': 'FEA',
        'id': 'FEA_01',
        'initial_wear': 0.15,
        'resilience_factor': 1.05,
        'base_wear_per_cycle': 0.0004,
        'failure_modes': {
            'FALHA_ELETRODO_A': {'probability_weight': 40, 'repair_time_hours': 8, 'repair_wear_reduction': 0.10},
            'SUPERAQUECIMENTO_MANCAL': {'probability_weight': 30, 'repair_time_hours': 12, 'repair_wear_reduction': 0.15},
            'FALHA_REFRIGERACAO_PAINEL': {'probability_weight': 20, 'repair_time_hours': 24, 'repair_wear_reduction': 0.05},
            'PROBLEMA_HIDRAULICO': {'probability_weight': 10, 'repair_time_hours': 6, 'repair_wear_reduction': 0.02}
        }
    },
    {
        'type': 'LF',
        'id': 'LF_01',
        'initial_wear': 0.08,
        'resilience_factor': 0.95,
        'base_wear_per_cycle': 0.0002,
        'failure_modes': {
            'FALHA_INJECAO_ARGONIO': {'probability_weight': 60, 'repair_time_hours': 4, 'repair_wear_reduction': 0.05},
            'DESGASTE_REFRATARIO': {'probability_weight': 40, 'repair_time_hours': 48, 'repair_wear_reduction': 0.40}
        }
    },
    {
        'type': 'CASTER',
        'id': 'CASTER_01',
        'initial_wear': 0.65, # Mantendo uma máquina já desgastada
        'resilience_factor': 1.0,
        'base_wear_per_cycle': 0.0008,
        'failure_modes': {
            'OBSTRUCAO_VALVULA': {'probability_weight': 50, 'repair_time_hours': 8, 'repair_wear_reduction': 0.08},
            'FALHA_MOLDE': {'probability_weight': 30, 'repair_time_hours': 16, 'repair_wear_reduction': 0.20},
            'PROBLEMA_ROLOS': {'probability_weight': 20, 'repair_time_hours': 24, 'repair_wear_reduction': 0.15}
        }
    }
]

# PARÂMETROS DO PRODUTO (PANELA)
LADLE_WEIGHT_KG = 120000.0
INITIAL_CHEMICAL_COMPOSITION = {
    "C_PERCENT": 0.05,
    "SI_PERCENT": 0.10,
    "MN_PERCENT": 0.20
}

# PARÂMETROS DE FALHA
# Multiplicador base para a probabilidade de falha.
FAILURE_PROBABILITY_MULTIPLIER = 0.2 # VALOR BEM MAIS ALTO

# Eventos Globais Súbitos
GLOBAL_EVENTS = {
    'SURTO_DE_TENSAO': {
        # Chance base de o evento começar a cada passo da simulação
        'base_probability_per_step': 0.001, # VALOR BEM MAIS ALTO
        # Duração do evento em passos de simulação (120 passos * 5s = 10 minutos)
        'duration_steps': 120,
        # Multiplicador de estresse: Aumenta a chance de falha em 50x durante o evento
        'failure_chance_multiplier': 50.0
    }
}