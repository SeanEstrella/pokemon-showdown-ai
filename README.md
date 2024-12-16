# Pokémon Showdown AI Battle Bot

This project implements a Generation I Pokémon battle bot for the Pokémon Showdown platform. The bot uses game theory concepts, including a heuristic inspired by Nash equilibrium, to make strategic decisions. It compares the performance of the heuristic-based strategy against a baseline damage-maximization strategy.

## Features

- **NashEquilibrium Strategy**: Implements heuristic-based decision-making inspired by Nash equilibrium.
- **MaxDamage Strategy**: A baseline bot that selects moves based on maximum damage output.
- **Battle Interface**: Connects to Pokémon Showdown using the `poke-env` framework.
- **Battle Runner**: Automates the execution of multiple battles and logs results for analysis.

---

## Requirements

- Python 3.9+
- [Poetry](https://python-poetry.org/) (for dependency management)

---

## Setup

### Clone the Repository

```bash
git clone https://github.com/SeanEstrella/pokemon-showdown-ai.git
cd pokemon-showdown-ai
```

### Install dependencies

```bash
poetry install
```

### Configure environment variables

- Edit a .env file and add the following.
- You will want to create pokemon showdown accounts for the bots you want to use.

```python
NASH_USERNAME=your_nash_username
NASH_PASSWORD=your_nash_password
MAX_USERNAME=your_max_username
MAX_PASSWORD=your_max_password
```

### Running multiple battles

- This is the current method for running the bots 

```bash
poetry run python src/run_multiple_battles.py
```

- You can also an alternative method for running the bots

```bash
poetry shell
python src/run_multiple_battles.py
```

