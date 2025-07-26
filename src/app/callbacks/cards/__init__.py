from .invalid_registers import register_invalid_registers
from .team_commitment import register_team_commitment
from .valid_registers import register_valid_registers


def register_cards_callbacks(app, app_state):
    register_invalid_registers(app, app_state)
    register_team_commitment(app, app_state)
    register_valid_registers(app, app_state)
