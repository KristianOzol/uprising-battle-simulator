
import sys
from loguru import logger

# Set the logging level to INFO (or any other higher level)
logger.remove()
logger.add(sys.stderr, level="INFO")  # Change "INFO" to the desired level

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import pandas as pd
import battle
from battle import Battle, BattleModifiers
import army
import uprising_units
import roll_modifier
import result_modifier
from battle_state import BattleResult

@dataclass
class MetaResults:
    data: pd.DataFrame

@dataclass
class ArmyConfig:
    army_type: army.Army
    units: list[uprising_units.Unit]

@dataclass
class BattleConfig:
    player_army_config: ArmyConfig
    enemy_army_config: ArmyConfig
    terrain: battle.Terrain
    battle_roll_modifications: list[roll_modifier.RollModification] 
    battle_result_modifications: list[result_modifier.ResultModification] 
class BattleOrchestrator:
    def __init__(self, battle_config: BattleConfig) -> None:
        self.player_army_config = battle_config.player_army_config
        self.enemy_army_config = battle_config.enemy_army_config
        self.terrain = battle_config.terrain
        self.roll_modifications = battle_config.battle_roll_modifications
        self.result_modifications = battle_config.battle_result_modifications
    
    def execute_battle(self) -> BattleResult:
        player_army: army.Army = self.player_army_config.army_type()
        for unit in self.player_army_config.units:
            player_army.add_unit(unit)
        enemy_army: army.Army = self.enemy_army_config.army_type()
        for unit in self.enemy_army_config.units:
            enemy_army.add_unit(unit)

        battle_modifiers = BattleModifiers(roll_modifier.RollModifier().add_modifications(self.roll_modifications),
                                           result_modifier.ResultModifier().add_modifications(self.result_modifications))
        battle: Battle = Battle(player_army, enemy_army, self.terrain, battle_modifiers)
        return battle.perform_battle()

    def conduct_battles(self, number_of_iterations: int = 5000) -> MetaResults:
        meta_results = MetaResults(data = pd.DataFrame())
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.execute_battle) for _ in range(number_of_iterations)]

            # Wait for all tasks to complete and check for errors
            for future in futures:
                battle_result: battle.BattleResult = future.result()
                new_row = pd.DataFrame({"overall_result": f"{battle_result.overall_result}, {battle_result.player_net_resources}",
                                        "victor": battle_result.overall_result,
                                        'net_resources': battle_result.player_net_resources}, index=[0])
                meta_results.data = pd.concat([meta_results.data, new_row], ignore_index=True)
        
        logger.info(f"Finished running {number_of_iterations}. Presenting dataframe:")
        return meta_results

player_config = ArmyConfig(army.TuaThanArmy, [uprising_units.Stoneshell, uprising_units.CrabRider, uprising_units.CrabRider, uprising_units.Harpooneers, uprising_units.Harpooneers])
enemy_config = ArmyConfig(army.ImperialArmy, [uprising_units.Garrison2])

terrain = battle.Terrain(battle.TerrainType.MARSHES)
battle_result_modifications: list[result_modifier.ResultModification] = [
    result_modifier.LightOfTheThan,
    result_modifier.TerrainResultModification,
    result_modifier.DruidMountainHeart,
    result_modifier.HarpoonersUpgrade
]
battle_roll_modifications = [roll_modifier.TerrainRollModification]
battle_config = BattleConfig(player_config, enemy_config, terrain, battle_roll_modifications, battle_result_modifications)
meta_battle = BattleOrchestrator(battle_config)
meta_results = meta_battle.conduct_battles()
#logger.info(meta_results)
# Calculate value counts and percentages
value_counts = meta_results.data['overall_result'].value_counts()
total_values = len(meta_results.data['overall_result'])
percentages = (value_counts / total_values) * 100

result_df = pd.DataFrame({'Count': value_counts, 'Percentage': percentages})
logger.info(f"This is the summary of the battle:")
logger.info(f"\n{result_df}")
