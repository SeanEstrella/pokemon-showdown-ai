from poke_env.data.gen_data import GenData
import json


def get_gen1_base_species_pokedex():
    return {
        name: data for name, data in pokedex.items()
        if 1 <= data["num"] <= 151 and "forme" not in data
        }


def dict_to_json(file_path, dictionary):
    try: 
        with open(file_path, 'w') as file:
            json_string = json.dumps(dictionary, default=lambda o: o.__dict__, sort_keys=True, indent=2)
            file.write(json_string)
    except FileExistsError: 
        print(f"The file '{file_path}' already exists.")


if __name__ == "__main__":
    gen1_data = GenData(1).from_gen(1)
    pokedex = gen1_data.load_pokedex(1)
    moves = gen1_data.load_moves(1)
    gen1_base_species_pokedex = get_gen1_base_species_pokedex()

    dict_to_json("src/data/moves.json", moves)
    dict_to_json("src/data/pokedex.json", gen1_base_species_pokedex)
