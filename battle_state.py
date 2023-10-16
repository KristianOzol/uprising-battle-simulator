from dataclasses import dataclass
from enum import StrEnum
import army
import dice

class TerrainType(StrEnum):
    MOUNTAIN = "Mountain"
    FOREST = "Forest"
    MARSHES = "Marshes"
    BADLANDS = "Badlands"
    FROZEN_WASTES = "Frozen Wastes"

class BattleStage(StrEnum):
    ARHCERY = "archery"
    CLASH = "clash"

class Terrain:
    def __init__(self, terrain_type: TerrainType) -> None:
        if terrain_type not in TerrainType:
            raise ValueError(f"Invalid terrain type. Valid options are: {', '.join([terrain.name for terrain in TerrainType])}")
        self.terrain_type = terrain_type

    def __str__(self):
        return f'Terrain type: {self.terrain_type.value}'

@dataclass
class BattleState:
    player_army: army.Army
    enemy_army: army.Army
    terrain: Terrain
    player_roll_results: dice.DiceRollResults = dice.DiceRollResults()
    enemy_roll_results: dice.DiceRollResults = dice.DiceRollResults()
    clash_round_number: int = 1
    battle_stage: BattleStage = BattleStage.ARHCERY

