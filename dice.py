from dataclasses import dataclass
from abc import abstractmethod
import dataclasses
import random
from loguru import logger

@dataclass(frozen=True)
class DiceNames:
    white = "White"
    orange = "Orange"
    blue = "Blue"
    red = "Red"
    purple = "Purple"
    black = "Black"
    bronze = "Bronze"
    silver = "Silver"
    gold = "Gold"

STANDARD_DICE_PRIORITY = [DiceNames.gold, 
                            DiceNames.silver, 
                            DiceNames.bronze, 
                            DiceNames.black, 
                            DiceNames.purple, 
                            DiceNames.blue, 
                            DiceNames.red, 
                            DiceNames.orange, 
                            DiceNames.white
]
STANDARD_LOSS_PRIORITY = [DiceNames.white,
                          DiceNames.orange,
                          DiceNames.red, 
                          DiceNames.blue, 
                          DiceNames.purple, 
                          DiceNames.black, 
                          DiceNames.bronze, 
                          DiceNames.silver,
                          DiceNames.gold 
]

@dataclass
class DieResult:
    skulls: int = 0
    shields: int = 0
    bolts: int = 0
    stars: int = 0
    blanks: int = 0

class DiceRollResults:
    def __init__(self) -> None:
        self.skulls: int = 0
        self.shields: int = 0
        self.bolts: int = 0
        self.stars: int = 0
        self.blanks: int = 0

        #self.results: dict[str, int] = {}
        #for field in dataclasses.fields(DieResult):
        #    field_name = field.name
        #    self.results[field_name] = 0

    def __repr__(self) -> str:
        return f"Skulls: {self.skulls}, Shields: {self.shields}, Bolts: {self.bolts}, Stars: {self.stars}, Blanks: {self.blanks}"

    def add_die_result(self, result: DieResult) -> None:
        self.skulls += result.skulls
        self.shields += result.shields
        self.bolts += result.bolts
        self.stars += result.stars
        self.blanks += result.blanks

@dataclass
class DieOutcomeDistribution:
    distribution: tuple[DieResult, DieResult, DieResult, DieResult, DieResult, DieResult]

class Die:
    def __init__(self) -> None:
        self.result: DieResult = None
        self.rerolled: bool = False

    @property
    @abstractmethod
    def die_outcome_distribution(self) -> DieOutcomeDistribution:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def __repr__(self) -> str:
        return self.name
    
    def roll(self) -> None:
        self.result = random.choice(self.die_outcome_distribution.distribution)


class WhiteDie(Die):    
    @property
    def die_outcome_distribution(self):
        return DieOutcomeDistribution(
            distribution = (DieResult(skulls=1, shields=1),
                            DieResult(skulls=1),
                            DieResult(shields=1),
                            DieResult(blanks=1),
                            DieResult(blanks=1),
                            DieResult(blanks=1))
        )
    @property
    def name(self):
        return DiceNames.white

class RedDie(Die):
    @property
    def die_outcome_distribution(self):
        return DieOutcomeDistribution(
            distribution = (DieResult(skulls=2),
                            DieResult(skulls=1, bolts=1),
                            DieResult(skulls=1),
                            DieResult(skulls=1),
                            DieResult(blanks=1),
                            DieResult(blanks=1))
        )
    @property
    def name(self):
        return DiceNames.red

class OrangeDie(Die):    
    @property
    def die_outcome_distribution(self):
        return DieOutcomeDistribution(
            distribution = (DieResult(skulls=1),
                            DieResult(skulls=1),
                            DieResult(skulls=1),
                            DieResult(skulls=1),
                            DieResult(blanks=1),
                            DieResult(blanks=1))
        )
    @property
    def name(self):
        return DiceNames.orange
    
class BlueDie(Die):    
    @property
    def die_outcome_distribution(self):
        return DieOutcomeDistribution(
            distribution = (DieResult(shields=1),
                            DieResult(shields=1),
                            DieResult(skulls=1),
                            DieResult(skulls=1),
                            DieResult(skulls=1),
                            DieResult(blanks=1))
        )
    @property
    def name(self):
        return DiceNames.blue
    
class PurpleDie(Die):    
    @property
    def die_outcome_distribution(self):
        return DieOutcomeDistribution(
            distribution = (DieResult(bolts=2),
                            DieResult(skulls=1, bolts=1),
                            DieResult(skulls=1),
                            DieResult(skulls=1),
                            DieResult(skulls=1),
                            DieResult(blanks=1))
        )
    @property
    def name(self):
        return DiceNames.purple

class BlackDie(Die):    
    @property
    def die_outcome_distribution(self):
        return DieOutcomeDistribution(
            distribution = (DieResult(skulls=3),
                            DieResult(skulls=2),
                            DieResult(skulls=1),
                            DieResult(skulls=1),
                            DieResult(skulls=1),
                            DieResult(bolts=1))
        )
    @property
    def name(self):
        return DiceNames.black

class DicePool:
    def __init__(self, reroll_count: int = 0, dice_reroll_priority: list[str] = STANDARD_DICE_PRIORITY):
        self.dice: list[Die] = []
        self.dice_count: dict[DiceNames, int] = {}
        self.reroll_count = reroll_count
        self.dice_reroll_priority = dice_reroll_priority

    def add_die(self, die: Die) -> "DicePool":
        self.dice.append(die)
        if die.name not in self.dice_count:
            self.dice_count[die.name] = 1
        else:
            self.dice_count[die.name] += 1
        return self
    
    def remove_die(self, die_type: DiceNames):
        if die_type not in self.dice_count:
            return
        for index, die in enumerate(self.dice):
            if die.name == die_type:
                del self.dice[index]
                self.dice_count[die_type] -= 1
                logger.debug(f"Removing {die} as it matches {die_type}")
                return

    def roll_dice(self) -> DiceRollResults:
        logger.debug(f"Rolling the following dice: {self.dice_count}")
        for die in self.dice:
            die.roll()

        total_result = DiceRollResults()
        for die in self.dice:
            total_result.add_die_result(die.result)

        return total_result


dice_pool = DicePool(reroll_count=2).add_die(BlueDie()).add_die(WhiteDie()).add_die(BlackDie()).add_die(PurpleDie())
logger.debug(dice_pool.roll_dice())
