import logging
import random
from typing import Optional

from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.pokemon import Pokemon
from poke_env.player.battle_order import BattleOrder
from poke_env.player.player import Player

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Common Gen 1 Status Moves that inflict a primary status
PARALYSIS_MOVES = ["thunderwave", "stunspore"]
SLEEP_MOVES = ["sleeppowder", "hypnosis", "sing", "spore", "lovelykiss"]
POISON_MOVES = ["poisonpowder", "toxic"]
CONFUSION_MOVES = [
    "confuseray",
    "supersonic",
]  # Confuse Ray and Supersonic cause confusion in Gen 1

# Stat-boosting moves in Gen 1
STAT_BOOST_MOVES = ["swordsdance", "amnesia"]

# Recovery moves in Gen 1
RECOVERY_MOVES = ["recover", "rest"]

# Reflect move in Gen 1
REFLECT_MOVE = ["reflect"]


class NashEquilibrium(Player):
    """
    A player implementation tailored to Gen 1 logic. It chooses moves based on a heuristic
    scoring system and considers switching if at a severe disadvantage.

    Key points:
    - Returns negative scores for redundant or already-applied status conditions.
    - Tracks the last used move and whether it was beneficial to avoid repeating ineffective moves.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_move_used = None
        self.last_move_effective = True

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:
        if not battle.available_moves:
            logger.debug("No available moves. Choosing a random move.")
            return self.choose_random_move(battle)

        opponent_pokemon = battle.opponent_active_pokemon

        # Log state for debugging
        logger.debug(f"Available moves: {[move.id for move in battle.available_moves]}")
        logger.debug(
            f"Active Pokemon HP: {battle.active_pokemon.current_hp}/{battle.active_pokemon.max_hp}"
        )
        logger.debug(
            f"Opponent Pokemon HP: {opponent_pokemon.current_hp}/{opponent_pokemon.max_hp}"
        )

        # Consider switching if at disadvantage
        if self.should_switch(battle):
            switch_order = self.choose_switch(battle)
            if switch_order:
                self.last_move_used = None
                self.last_move_effective = True
                return switch_order

        # Score all available moves and pick the best
        scored_moves = []
        for move in battle.available_moves:
            score = self.score_move(move, battle)
            scored_moves.append((move, score))

        # Log scores for debugging
        for move, score in scored_moves:
            logger.debug(f"Move {move.id} score: {score:.2f}")

        best_move, best_score = max(scored_moves, key=lambda x: x[1])

        # If repeating the same ineffective move, penalize further
        if best_move.id.lower() == self.last_move_used and best_score <= 0.0:
            best_score -= 0.5

        # Record chosen move info
        chosen_move = best_move
        self.last_move_used = chosen_move.id.lower()
        self.last_move_effective = best_score > 0.0

        logger.debug(f"Selected move: {chosen_move.id}")
        return self.create_order(chosen_move)

    def should_switch(self, battle: AbstractBattle) -> bool:
        if not battle.available_switches or not battle.available_moves:
            return False

        active_pokemon = battle.active_pokemon
        opponent = battle.opponent_active_pokemon
        type_effectiveness = sum(
            opponent.damage_multiplier(move) for move in battle.available_moves
        ) / len(battle.available_moves)

        # If we are at a severe disadvantage (low type effectiveness and low HP), consider switching
        return type_effectiveness < 0.5 and active_pokemon.current_hp_fraction < 0.5

    def choose_switch(self, battle: AbstractBattle) -> Optional[BattleOrder]:
        if not battle.available_switches:
            return None

        scored_switches = [
            (pokemon, self.score_switch(pokemon, battle))
            for pokemon in battle.available_switches
        ]

        best_switch = max(scored_switches, key=lambda x: x[1])[0]
        logger.debug(f"Switching to: {best_switch.species}")
        return self.create_order(best_switch)

    def score_switch(self, pokemon: Pokemon, battle: AbstractBattle) -> float:
        opponent = battle.opponent_active_pokemon

        # Defensive score: negative if we take more damage
        defensive_score = 0.0
        for opp_move in opponent.moves.values():
            if opp_move.category != MoveCategory.STATUS:
                defensive_score -= pokemon.damage_multiplier(opp_move)

        # Offensive score: positive if we deal more damage
        offensive_score = 0.0
        for pkmn_move in pokemon.moves.values():
            if pkmn_move.category != MoveCategory.STATUS:
                offensive_score += opponent.damage_multiplier(pkmn_move)

        hp_factor = pokemon.current_hp_fraction or 1.0
        return (defensive_score + offensive_score) * hp_factor

    def score_move(self, move: Move, battle: AbstractBattle) -> float:
        # Separate logic for status and attacking moves
        if move.category == MoveCategory.STATUS:
            return self.score_status_move(move, battle)

        attacker = battle.active_pokemon
        defender = battle.opponent_active_pokemon
        damage_estimate = self.calculate_damage(move, attacker, defender)

        defender_current_hp = (
            defender.current_hp
            if defender.current_hp is not None
            else (defender.max_hp or 100)
        )
        accuracy_factor = (move.accuracy / 100.0) if move.accuracy else 1.0

        effective_score = (
            damage_estimate / (defender_current_hp + 1.0)
        ) * accuracy_factor
        return effective_score

    def score_status_move(self, move: Move, battle: AbstractBattle) -> float:
        base_score = 50.0
        move_id = move.id.lower()
        opponent = battle.opponent_active_pokemon
        active = battle.active_pokemon

        # Define all major statuses in Gen 1 that matter for avoiding stacking:
        MAJOR_STATUSES = {"par", "slp", "psn", "tox", "brn", "frz"}

        # If opponent already has a major status, no need to use a move that inflicts another one.
        # Check if the move is one of the major-status-inflicting moves:
        if (
            move_id in PARALYSIS_MOVES
            or move_id in SLEEP_MOVES
            or move_id in POISON_MOVES
        ):
            if opponent.status in MAJOR_STATUSES:
                return -1.0

        # Handle major statuses
        if move_id in PARALYSIS_MOVES:
            # If already paralyzed, don't do it again
            if opponent.status == "par":
                return -1.0
            return base_score * 1.1

        if move_id in SLEEP_MOVES:
            # If already asleep, don't do it again
            if opponent.status == "slp":
                return -1.0
            return base_score * 1.1

        if move_id in POISON_MOVES:
            # If already poisoned, don't do it again
            if opponent.status in ["psn", "tox"]:
                return -1.0
            return base_score * 1.1

        if move_id in CONFUSION_MOVES:
            # Confusion is not a major status, but we penalize repeating if not effective
            if (
                self.last_move_used
                and self.last_move_used in CONFUSION_MOVES
                and not self.last_move_effective
            ):
                return -1.0
            return base_score

        # Stat-boosting moves
        if move_id in STAT_BOOST_MOVES:
            if "swordsdance" in move_id:
                if active.boosts.get("atk", 0) < 6:
                    return base_score * 1.5
                return -1.0
            if "amnesia" in move_id:
                if active.boosts.get("spa", 0) < 6:
                    return base_score * 1.5
                return -1.0

        # Recovery moves
        if any(heal in move_id for heal in RECOVERY_MOVES):
            hp_fraction = active.current_hp_fraction
            if hp_fraction < 1.0:
                if hp_fraction < 0.4:
                    return base_score * (1.0 - hp_fraction)
                return base_score * 0.3
            return -1.0

        # Reflect
        if move_id in REFLECT_MOVE:
            if "reflect" in battle.side_conditions:
                return -1.0
            return base_score * 1.2

        # Default for other status moves
        if not self.last_move_effective and self.last_move_used == move.id:
            return -1.0

        return base_score * 0.8

    def calculate_damage(
        self,
        move: Move,
        attacker: Pokemon,
        defender: Pokemon,
    ) -> float:
        # Fixed damage moves
        if move.damage is not None:
            if isinstance(move.damage, int):
                return float(move.damage)
            if isinstance(move.damage, str) and move.damage.lower() == "level":
                return float(attacker.level or 100)
            return 0.0

        level = attacker.level or 100
        power = move.base_power or 0

        # In Gen 1, Special is unified. We'll use spa for both offense and defense.
        if move.category == MoveCategory.PHYSICAL:
            attack = attacker.stats.get("atk", 100)
            defense = defender.stats.get("def", 100)
        elif move.category == MoveCategory.SPECIAL:
            attack = attacker.stats.get("spa", 100)
            defense = defender.stats.get("spa", 100)
        else:
            # Status moves do no direct damage
            return 0.0

        damage = (((2 * level / 5 + 2) * power * (attack / defense)) / 50) + 2

        # STAB (Same-Type Attack Bonus)
        if move.type and move.type in attacker.types:
            damage *= 1.5

        # Type effectiveness
        damage *= defender.damage_multiplier(move)

        # Random variation
        damage *= random.uniform(0.85, 1.0)  # nosec B311

        return max(1.0, damage)
