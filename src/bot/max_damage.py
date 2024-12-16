from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.player.battle_order import BattleOrder
from poke_env.player.player import Player
from poke_env.ps_client.account_configuration import AccountConfiguration


class MaxDamagePlayer(Player):
    def __init__(self, *args: AccountConfiguration, **kwargs: int):
        super().__init__(*args, **kwargs)

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:
        if battle.available_moves:
            best_move = max(battle.available_moves, key=lambda move: move.base_power)
            return self.create_order(best_move)
        return self.choose_random_move(battle)
