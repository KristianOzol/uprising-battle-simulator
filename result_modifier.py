from abc import abstractmethod
from enum import StrEnum
import dice
from loguru import logger

from battle_state import BattleState, TerrainType, BattleStage

class ResultModificationTarget(StrEnum):
    PLAYER = "Player"
    ENEMY = "Enemy"

class ResultModification:
    def __init__(self) -> None:
        self.once_per_combat: bool
        self.once_per_round: bool
        self.used_this_combat: bool
        self.used_this_round: bool

    @property
    @abstractmethod
    def name(self) -> int:
        pass

    def __repr__(self) -> str:
        return self.name
    
    @abstractmethod
    def modify_result(self, current_battle_state: BattleState) -> None:
        pass

class ResultModifier:
    def __init__(self) -> None:
        self.modification_list: list[ResultModification] = []
    
    def add_modification(self, modification: ResultModification) -> "ResultModifier":
        self.modification_list.append(modification())
        return self

    def apply_modifications(self, current_battle_state: BattleState) -> None:
        for modification in self.modification_list:
            modification.modify_result(current_battle_state)


class RerollModification(ResultModification):
    def __init__(self, target: ResultModificationTarget, reroll_count: int, reroll_priority: list[dice.DiceNames] = dice.STANDARD_DICE_PRIORITY) -> None:
        super().__init__()
        self.target = target
        self.reroll_count = reroll_count
        self.reroll_priority = reroll_priority

    def reroll_die(self, dice_pool: dice.DicePool, dice_results: dice.DiceRollResults):
        for dice_type_name in self.reroll_priority:
            for die in dice_pool.dice:
                if die.name == dice_type_name and not die.rerolled and die.result.blanks == 1:
                    logger.debug(f"Rerolling dice {die.name} with result {die.result}")
                    dice_results.blanks -= 1
                    die.roll()
                    die.rerolled = True
                    dice_results.add_die_result(die.result)
                    logger.debug(f"New result: {die.result}")
                    return

    def reroll_dice(self, dice_pool: dice.DicePool, dice_results: dice.DiceRollResults) -> None:
        if dice_results.blanks == 0:
            logger.debug(f"No blanks to reroll")
            return
    
        for _ in range(self.reroll_count):
            self.reroll_die(dice_pool, dice_results)
        for die in dice_pool.dice:
            die.rerolled = False
        logger.debug(f"New dice roll results after rerolling: {dice_results}")
    
    def modify_result(self, current_battle_state: BattleState) -> None:
        logger.debug(f"Rerolling dice (with reroll count {self.reroll_count}) for {self.target}")
        if self.target == ResultModificationTarget.PLAYER:
            self.reroll_dice(current_battle_state.player_army.current_dice_pool, current_battle_state.player_roll_results)
        else:
            self.reroll_dice(current_battle_state.enemy_army.current_dice_pool, current_battle_state.enemy_roll_results)

def player_will_take_damage(state: BattleState) -> bool:
    if (state.player_roll_results.shields - state.enemy_roll_results.bolts) < state.enemy_roll_results.skulls:
        logger.debug(f"The enemy will deal damage to the player units without intervention")
        return True
    logger.debug(f"The player will not take damage from the enemy roll")
    return False

class DruidMountainHeart(ResultModification):
    def ignore_skulls_of_single_die(self, state: BattleState) -> None:
        for skull_number in [3, 2, 1]:
            for die in state.enemy_army.current_dice_pool.dice:
                if die.result.skulls == skull_number:
                    logger.debug(f"Mountain Heart power ignored skulls on die {die} with result {die.result}")
                    state.enemy_roll_results.skulls -= skull_number
                    state.player_roll_results.bolts -= 1
                    return

    def modify_result(self, state: BattleState) -> None:
        if state.player_roll_results.bolts >= 1 and player_will_take_damage(state):
            self.ignore_skulls_of_single_die(state)
            logger.debug(f"The enemy now has the following result after Mountain Heart modification: {state.enemy_roll_results}")

class TerrainResultModification(ResultModification):
    def modify_result(self, current_battle_state: BattleState) -> None:
        if current_battle_state.battle_stage == BattleStage.ARHCERY:
            if current_battle_state.terrain.terrain_type == TerrainType.FOREST:
                logger.debug("Fighting in forest, rerolls blanks for best dice")
                RerollModification(ResultModificationTarget.PLAYER, 2).modify_result(current_battle_state)
                RerollModification(ResultModificationTarget.ENEMY, 2).modify_result(current_battle_state)
                
                