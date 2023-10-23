from __future__ import annotations
from abc import abstractmethod
from enum import StrEnum
import dice
from dice import BlueDie, Die, WhiteDie, OrangeDie
from loguru import logger

class UnitTypes(StrEnum):
    elite_rider = "Elite Rider"
    basic_rider = "Basic Rider"
    basic_warrior = "Basic Warrior"
    elite_warrior = "Elite Warrior"
    basic_archer = "Basic Archer"
    elite_archer = "Elite Archer"
    no_type = "Untyped"

class Unit:
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def __init__(self) -> None:
        self.archery_dice: list[dice.Die]
        self.clash_dice: list[dice.Die]
        self.initialize_clash_dice()
        self.initialize_archery_dice()

    @abstractmethod
    def initialize_clash_dice(self) -> list[Die]:
        pass

    @abstractmethod
    def initialize_archery_dice(self) -> list[Die]:
        pass

    @classmethod
    @property
    @abstractmethod
    def cost(cls) -> int:
        pass

    @classmethod
    @property
    @abstractmethod
    def unit_type(cls) -> int:
        pass

    def __repr__(self) -> str:
        return self.name

class Garrison1(Unit):
    def __init__(self) -> None:
        super().__init__()

    def initialize_archery_dice(self) -> None:
        self.archery_dice = [WhiteDie()]
        
    def initialize_clash_dice(self) -> None:
        self.clash_dice = [WhiteDie(), BlueDie()]

    @classmethod
    @property
    def cost(cls) -> int:
        return 0

    @classmethod
    @property
    def name(cls) -> str:
        return "Garrison1"
    
    @classmethod
    @property
    def unit_type(cls) -> str:
        return UnitTypes.no_type

class Garrison2(Unit):
    def __init__(self) -> None:
        super().__init__()

    def initialize_archery_dice(self) -> None:
        self.archery_dice = [WhiteDie(), WhiteDie()]
        
    def initialize_clash_dice(self) -> None:
        self.clash_dice = [WhiteDie(), BlueDie(), OrangeDie(), OrangeDie()]

    @classmethod
    @property
    def cost(cls) -> int:
        return 0

    @classmethod
    @property
    def name(cls) -> str:
        return "Garrison2"
    
    @classmethod
    @property
    def unit_type(cls) -> str:
        return UnitTypes.no_type
    
class Garrison3(Unit):
    def __init__(self) -> None:
        super().__init__()

    def initialize_archery_dice(self) -> None:
        self.archery_dice = [WhiteDie(), WhiteDie(), WhiteDie()]
        
    def initialize_clash_dice(self) -> None:
        self.clash_dice = [WhiteDie(), BlueDie(), BlueDie(), OrangeDie(), OrangeDie()]

    @classmethod
    @property
    def cost(cls) -> int:
        return 0

    @classmethod
    @property
    def name(cls) -> str:
        return "Garrison3"
    
    @classmethod
    @property
    def unit_type(cls) -> str:
        return UnitTypes.no_type

class Stoneshell(Unit):
    def __init__(self) -> None:
        super().__init__()

    def initialize_archery_dice(self) -> None:
        self.archery_dice = []
        
    def initialize_clash_dice(self) -> None:
        self.clash_dice = [WhiteDie()]

    @classmethod
    @property
    def cost(cls) -> int:
        return 2

    @classmethod
    @property
    def name(cls) -> str:
        return "Stoneshell"
    
    @classmethod
    @property
    def unit_type(cls) -> str:
        return UnitTypes.basic_warrior
    
class CrabRider(Unit):
    def __init__(self) -> None:
        super().__init__()

    def initialize_archery_dice(self) -> None:
        self.archery_dice = []
        
    def initialize_clash_dice(self) -> None:
        self.clash_dice = [BlueDie()]

    @classmethod
    @property
    def cost(cls) -> int:
        return 2

    @classmethod
    @property
    def name(cls) -> str:
        return "CrabRider"
    
    @classmethod
    @property
    def unit_type(cls) -> str:
        return UnitTypes.basic_rider

class Harpooneers(Unit):
    def __init__(self) -> None:
        super().__init__()
        self.food_generated_this_combat: bool = False

    def initialize_archery_dice(self) -> None:
        self.archery_dice = []
        
    def initialize_clash_dice(self) -> None:
        self.clash_dice = [dice.PurpleDie()]

    @classmethod
    @property
    def cost(cls) -> int:
        return 5

    @classmethod
    @property
    def name(cls) -> str:
        return "Harpooneers"
    
    @classmethod
    @property
    def unit_type(cls) -> str:
        return UnitTypes.elite_warrior


class ReefKing(Unit):
    def __init__(self) -> None:
        super().__init__()

    def initialize_archery_dice(self) -> None:
        self.archery_dice = [dice.BlackDie()]
        
    def initialize_clash_dice(self) -> None:
        self.clash_dice = [dice.BlackDie()]

    @classmethod
    @property
    def cost(cls) -> int:
        return 9

    @classmethod
    @property
    def name(cls) -> str:
        return "Reef King"
    
    @classmethod
    @property
    def unit_type(cls) -> str:
        return UnitTypes.elite_archer

garrison_level_1 = Garrison1()
logger.debug(garrison_level_1.clash_dice)
logger.debug(UnitTypes.basic_archer)