
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
    battle_modifiers: BattleModifiers

class BattleOrchestrator:
    def __init__(self, battle_config: BattleConfig) -> None:
        self.player_army_config = battle_config.player_army_config
        self.enemy_army_config = battle_config.enemy_army_config
        self.terrain = battle_config.terrain
        self.battle_modifiers = battle_config.battle_modifiers

    def execute_battle(self) -> battle.OverallBattleResult:
        player_army: army.Army = self.player_army_config.army_type()
        for unit in self.player_army_config.units:
            player_army.add_unit(unit)
        enemy_army: army.Army = self.enemy_army_config.army_type()
        for unit in self.enemy_army_config.units:
            enemy_army.add_unit(unit)

        battle: Battle = Battle(player_army, enemy_army, self.terrain, self.battle_modifiers)
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
        
        logger.debug(f"Finished running {number_of_iterations}. Presenting dataframe:")
        #logger.debug(meta_results.data)
        return meta_results

player_config = ArmyConfig(army.TuaThanArmy, [uprising_units.CrabRider, uprising_units.CrabRider, uprising_units.Harpooneers, uprising_units.Harpooneers, uprising_units.ReefKing])
enemy_config = ArmyConfig(army.ImperialArmy, [uprising_units.Garrison2])
terrain = battle.Terrain(battle.TerrainType.FROZEN_WASTES)
battle_result_modifier = result_modifier.ResultModifier().add_modification(
    result_modifier.TerrainResultModification).add_modification(result_modifier.DruidMountainHeart)
battle_modifier = BattleModifiers(roll_modifier.RollModifier().add_modification(roll_modifier.TerrainRollModification), 
                                  battle_result_modifier)
battle_config = BattleConfig(player_config, enemy_config, terrain, battle_modifier)
meta_battle = BattleOrchestrator(battle_config)
meta_results = meta_battle.conduct_battles()

# Calculate value counts and percentages
value_counts = meta_results.data['overall_result'].value_counts()
total_values = len(meta_results.data['overall_result'])
percentages = (value_counts / total_values) * 100

result_df = pd.DataFrame({'Count': value_counts, 'Percentage': percentages})
logger.info(f"This is the summary of the battle:")
logger.info(f"\n{result_df}")
