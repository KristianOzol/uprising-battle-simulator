from abc import abstractmethod
from dataclasses import dataclass
from enum import StrEnum
import army
import dice
import uprising_units
from battle_state import Terrain, BattleState, BattleStage, TerrainType
from roll_modifier import RollModifier, TerrainRollModification
from result_modifier import ResultModifier, TerrainResultModification, DruidMountainHeart
from loguru import logger

class OverallBattleResult(StrEnum):
    player_victory = "Player victory!"
    draw = "Draw!"
    player_defeat = "Player defeat!"
    undecided = "Undecided"

@dataclass
class BattleResult:
    player_net_resources = 0
    overall_result: str = OverallBattleResult.undecided

    def __repr__(self) -> str:
       return f"{self.overall_result} Net resources: {self.player_net_resources}"
@dataclass
class BattleModifiers:
    roll_modifier: RollModifier
    result_modifier: ResultModifier

class Battle:
    def __init__(self, player_army: army.Army, enemy_army: army.Army, terrian: Terrain, battle_modifiers: BattleModifiers) -> None:
        self.battle_state: BattleState = BattleState(player_army, enemy_army, terrian)
        self.roll_modifier = battle_modifiers.roll_modifier
        self.result_modifier = battle_modifiers.result_modifier
        self.initial_player_value: int = player_army.get_army_value()
        self.player_lost_value: int = 0
        self.battle_results: BattleResult = BattleResult()
        logger.debug(f"Setting up battle between {self.battle_state.player_army} with {self.battle_state.player_army.units}\
                     and {self.battle_state.enemy_army} with {self.battle_state.enemy_army.units}")

    def resolve_roll_result_effects(self):
        player_losses = self.battle_state.enemy_roll_results.skulls - (self.battle_state.player_roll_results.shields - self.battle_state.enemy_roll_results.bolts)
        enemy_losses = self.battle_state.player_roll_results.skulls - (self.battle_state.enemy_roll_results.shields - self.battle_state.player_roll_results.bolts)
        self.battle_state.player_army.take_loses(player_losses)
        self.battle_state.enemy_army.take_loses(enemy_losses)
        
    def update_net_resources(self):
        round_loss = (self.initial_player_value - self.player_lost_value) - self.battle_state.player_army.get_army_value()
        self.player_lost_value += round_loss
        logger.debug(f"Lost value due to the current round: {round_loss}")
        self.battle_results.player_net_resources -= round_loss

    def archery_round(self):
        player_dice = self.battle_state.player_army.collect_army_dice_archery()
        enemy_dice = self.battle_state.enemy_army.collect_army_dice_archery()
        self.roll_modifier.apply_modifications(self.battle_state)

        self.battle_state.player_roll_results = player_dice.roll_dice()
        logger.debug(f"Player rolled following dice: {self.battle_state.player_roll_results}")
        self.battle_state.enemy_roll_results = enemy_dice.roll_dice()
        logger.debug(f"Enemy rolled following dice: {self.battle_state.enemy_roll_results}")
        self.result_modifier.apply_modifications(self.battle_state)
        self.resolve_roll_result_effects()
        self.update_net_resources()
        
    def clash_round(self):
        logger.debug(f"Performing clash round number {self.battle_state.clash_round_number}")
        player_dice = self.battle_state.player_army.collect_army_dice_clash()
        enemy_dice = self.battle_state.enemy_army.collect_army_dice_clash()
        self.roll_modifier.apply_modifications(self.battle_state)

        self.battle_state.player_roll_results = player_dice.roll_dice()
        logger.debug(f"Player rolled following dice: {self.battle_state.player_roll_results}")
        self.battle_state.enemy_roll_results = enemy_dice.roll_dice()
        logger.debug(f"Enemy rolled following dice: {self.battle_state.enemy_roll_results}")
        self.result_modifier.apply_modifications(self.battle_state)

        self.resolve_roll_result_effects()
        self.update_net_resources()
        if not self.is_battle_over():
            self.battle_state.clash_round_number += 1
            self.clash_round()

    def is_battle_over(self):
        if len(self.battle_state.player_army.units) == 0 and len(self.battle_state.enemy_army.units) == 0:
            self.battle_results.overall_result = OverallBattleResult.draw
            return True
        if len(self.battle_state.player_army.units) == 0:
            self.battle_results.overall_result = OverallBattleResult.player_defeat
            return True
        if len(self.battle_state.enemy_army.units) == 0:
            self.battle_results.overall_result = OverallBattleResult.player_victory
            return True
        return False
    
    def perform_battle(self) -> BattleResult:
        logger.debug(f"Performing archery round!")
        self.archery_round()
        
        if self.is_battle_over():
            return self.battle_results
        
        self.battle_state.battle_stage = BattleStage.CLASH
        logger.debug("Performing clash rounds!")
        self.clash_round()
        
        return self.battle_results

imp_army = army.ImperialArmy().add_garrison_level_3()

#tua_army = TuaThanArmy().add_unit(units.Stoneshell.name).add_unit(units.CrabRider.name).add_unit(units.CrabRider.name)
tua_army = army.TuaThanArmy().add_unit(uprising_units.CrabRider, 2).add_unit(uprising_units.Harpooneers, 2).add_unit(uprising_units.ReefKing)
battle_modifiers = BattleModifiers(RollModifier().add_modification(TerrainRollModification), ResultModifier().add_modification(TerrainResultModification).add_modification(DruidMountainHeart))
battle = Battle(tua_army, imp_army, Terrain(TerrainType.FOREST), battle_modifiers)
results = battle.perform_battle()
logger.debug(results)

