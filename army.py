from __future__ import annotations
from abc import abstractmethod
from typing import override
from loguru import logger
import uprising_units
import dice
from dice import STANDARD_LOSS_PRIORITY

class Army:
    def __init__(self) -> None:
        self.current_dice_pool: dice.DicePool
        self.mercy: bool = False

    @abstractmethod
    def collect_army_dice_archery(self) -> dice.DicePool:
        pass

    @abstractmethod
    def collect_army_dice_clash(self) -> dice.DicePool:
        pass

    @abstractmethod
    def take_loses(self, loss_count: int):
        pass

    @abstractmethod
    def get_army_value(self) -> int:
        pass

    @abstractmethod
    def get_hit_points(self) -> int:
        pass

class EntityArmy(Army):
    pass

class UnitsArmy(Army):
    def __init__(self) -> None:
        super().__init__()
        self.units: list[uprising_units.Unit] = []
        self.loss_priority: list[dice.DiceNames] = STANDARD_LOSS_PRIORITY

    def add_unit(self, unit_class: uprising_units.Unit, count: int = 1) -> "Army":
        for _ in range(count):
            if len(self.units) == 5:
                logger.debug("Cannot add more units to army, already at max capacity of 5")
                return self
            self.units.append(unit_class())
        logger.debug(f"Added {count} {unit_class.name} to the unit list")
        return self
    
    def collect_army_dice_archery(self) -> dice.DicePool:
        pool = dice.DicePool()
        for unit in self.units:
            for die in unit.archery_dice:
                pool.add_die(die)
        self.current_dice_pool = pool
        logger.debug(f"Army with units {self.units} has the following archery dice: {pool.dice_count}")
        return pool
    
    def collect_army_dice_clash(self) -> dice.DicePool:
        pool = dice.DicePool()
        for unit in self.units:
            for die in unit.clash_dice:
                pool.add_die(die)
        self.current_dice_pool = pool
        logger.debug(f"Army with units {self.units} has the following clash dice: {pool.dice_count}")
        return pool
    
    def remove_worst_unit(self) -> None:
        for dice_type in self.loss_priority:
            for index, unit in enumerate(self.units):
                if len(unit.clash_dice) == 1:
                    if unit.clash_dice[0].name == dice_type:
                        logger.debug(f"Removing {unit} with die {unit.clash_dice[0]} as it matches {dice_type}")
                        del self.units[index]
                        return

    def take_loses(self, loss_count: int):
        for _ in range(loss_count):
            if len(self.units) == 0:
                logger.debug(f"No more units to remove from army {self}")
                break
            self.remove_worst_unit()

    def get_army_value(self) -> int:
        value = 0
        for unit in self.units:
            value += unit.cost
        return value
    
    def get_hit_points(self) -> int:
        return len(self.units)
    
    # def get_implicit_godpower(self) -> result_modifier.ResultModification:
    #     for unit in self.units:
    #         if unit.godpower:
    #             return unit.godpower 

class ImperialArmy(UnitsArmy):
    def __init__(self) -> None:
        super().__init__()

        self.loss_actions = {
            uprising_units.Garrison1.name: self.garison1_loss,
            uprising_units.Garrison2.name: self.garison2_loss,
            uprising_units.Garrison3.name: self.garison3_loss
        }

    @override
    def take_loses(self, loss_count: int) -> None:
        for _ in range(loss_count):
            if len(self.units) == 0:
                logger.debug("No more imperial units left to remove")
                break

            action_func = self.loss_actions.get(self.units[0].name)
            action_func()
        return

    def get_hit_points(self) -> int:
        if len(self.units) == 0:
            return 0
        return self.units[0].name[-1]
    
    def garison1_loss(self):
        self.units = []
        logger.debug("Removed last garrison from imperial army")

    def garison2_loss(self):
        self.units = [uprising_units.Garrison1()]
        logger.debug("Downgraded garrison 2 to a garrison 1")

    def garison3_loss(self):
        self.units = [uprising_units.Garrison2()]
        logger.debug("Downgraded garrison 3 to a garrison 2")
            
    def add_garrison_level_1(self) -> "ImperialArmy":
        self.units = [uprising_units.Garrison1()]
        return self
    
    def add_garrison_level_2(self) -> "ImperialArmy":
        self.units = [uprising_units.Garrison2()]
        return self
    
    def add_garrison_level_3(self) -> "ImperialArmy":
        self.units = [uprising_units.Garrison3()]
        return self

def main():
    imp_army = ImperialArmy().add_unit(uprising_units.Garrison3)

    imp_army.collect_army_dice_clash()

    imp_army.take_loses(1)

    imp_army.collect_army_dice_clash()

    #tua_army = TuaThanArmy().add_unit(units.Stoneshell.name).add_unit(units.CrabRider.name).add_unit(units.CrabRider.name)
    tua_army = UnitsArmy().add_unit(uprising_units.Stoneshell, 2).add_unit(uprising_units.CrabRider, 2)

    tua_army.collect_army_dice_clash()

    tua_army.take_loses(5)

main()