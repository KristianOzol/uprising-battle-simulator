from __future__ import annotations
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

class OverallBattleResult(StrEnum):
    player_victory = "Player victory!"
    draw = "Draw!"
    player_defeat = "Player defeat!"
    undecided = "Undecided"
class BattleResult:
    def __init__(self) -> None:
        self.player_net_resources = 0
        self.overall_result: str = OverallBattleResult.undecided

    def __repr__(self) -> str:
       return f"{self.overall_result} Net resources: {self.player_net_resources}"

@dataclass
class BattleState:
    player_army: army.Army
    enemy_army: army.Army
    terrain: Terrain
    battle_results: BattleResult
    player_roll_results: dice.DiceRollResults = dice.DiceRollResults()
    enemy_roll_results: dice.DiceRollResults = dice.DiceRollResults()
    clash_round_number: int = 1
    battle_stage: BattleStage = BattleStage.ARHCERY
