from abc import abstractmethod
import dice
from loguru import logger
import army
from battle_state import BattleState, TerrainType, BattleStage

class RollModification:
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
    def modify_roll(self, current_battle_state: BattleState) -> None:
        pass

class RollModifier:
    def __init__(self) -> None:
        self.modification_list: list[RollModification] = []
    
    def add_modification(self, modification: RollModification) -> "RollModifier":
        self.modification_list.append(modification())
        return self

    def apply_modifications(self, current_battle_state: BattleState) -> None:
        for modification in self.modification_list:
            modification.modify_roll(current_battle_state)

class TerrainRollModification(RollModification):
    def add_rider_dice(self, army: army.Army) -> None:
        for unit in army.units:
            if "Rider" in unit.unit_type:
                for die in unit.clash_dice:
                    army.current_dice_pool.add_die(die)

    def convert_red_to_white(self, army: army.Army) -> None:
        for die in army.current_dice_pool.dice:
            if die.name == dice.DiceNames.red:
                logger.debug("Found red die in dice pool, converting to white")
                army.current_dice_pool.remove_die(dice.DiceNames.red)
                army.current_dice_pool.add_die(dice.WhiteDie())

    def remove_all_but_one_die(self, dice_pool: dice.DicePool) -> None:
        if len(dice_pool.dice) <= 1:
            logger.debug(f"No need to remove dice from {dice_pool}")
            return
        while (len(dice_pool.dice) > 1):
            for dice_type in dice.STANDARD_LOSS_PRIORITY:
                dice_pool.remove_die(dice_type)

    def modify_roll(self, current_battle_state: BattleState) -> None:
        if current_battle_state.battle_stage == BattleStage.ARHCERY:
            if current_battle_state.terrain.terrain_type == TerrainType.MOUNTAIN:
                logger.debug("Fighting in mountains, removing all but one dice")
                self.remove_all_but_one_die(current_battle_state.player_army.current_dice_pool)
                self.remove_all_but_one_die(current_battle_state.enemy_army.current_dice_pool)
            if current_battle_state.terrain.terrain_type == TerrainType.BADLANDS:
                logger.debug("Fighting in badlands, adding rider dice")
                self.add_rider_dice(current_battle_state.player_army)
                self.add_rider_dice(current_battle_state.enemy_army)
        
        if current_battle_state.terrain.terrain_type == TerrainType.MARSHES:
            logger.debug("Fighting in marshes, converting red to white dice")
            self.convert_red_to_white(current_battle_state.player_army)
            self.convert_red_to_white(current_battle_state.enemy_army)
