from poke_env import AccountConfiguration, ShowdownServerConfiguration
from src.config.settings import USERNAME, PASSWORD, GEN_1_FORMAT
from src.bot.max_damage import MaxDamagePlayer

import asyncio
import logging


async def main():
    player = MaxDamagePlayer(
        account_configuration=AccountConfiguration(USERNAME, PASSWORD),
        server_configuration=ShowdownServerConfiguration,
        log_level=logging.DEBUG,
        battle_format=GEN_1_FORMAT,)

    await player.ladder(1)

    for battle in player.battles.values():
        print(battle.rating, battle.opponent_rating)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
