#!/usr/bin/python

from enum import Enum
import json
import openapi_client
from openapi_client.models.race import Race
from openapi_client.rest import ApiException
from pprint import pprint

class race:
    def __init__(self,name):
        self.name = name
        self.subtype = ""
        self.size = ""
        self.traits = []
        self.actions = []
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
configuration = openapi_client.Configuration(
    host = "https://www.dnd5eapi.co"
)
all_races = []
gradio_ui_elements = {}
def load_rest_data():
    if len(all_races) ==0 :
        print('Loading data from API')
        for _race in World.RACES.value:
            print(f'Trying to get data for the {_race}')
            # Enter a context with an instance of the API client
            with openapi_client.ApiClient(configuration) as api_client:
                # Create an instance of the API class
                api_instance = openapi_client.RacesApi(api_client)

                try:
                    # Get a race by index.
                    api_response = api_instance.api_races_index_get(_race)
                    # print("The response of RacesApi->api_races_index_get:\n")
                    # pprint(api_response)
                    all_races.append(api_response)
                except Exception as e:
                    print("Exception when calling RacesApi->api_races_index_get: %s\n" % e)
        print('done')
        pprint(all_races)
class World(Enum):
    RACES = ["dwarf", "elf", "halfling", "human", "dragonborn", "gnome", \
        "half-elf", "half-orc", "tiefling"]
    R_SH = ["dwa", "elf", "halfling", "hum", "dra", "gno", "halfelf", \
        "halforc", "tiefling"]
    CLASSES = ["Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", \
        "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"]
    CL_SH = ["barb", "bard", "cler", "dru", "fig", "monk", "pal", "rang", \
        "rogue", "sorc", "warl", "wiz"]
    ALIG = ["Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", \
        "True Neutral", "Chaotic Neutral", "Lawful Evil", \
        "Neutral Evil", "Chaotic Evil"]
    ALIG_CHART = [["Lawful", "Neutral", "Chaotic"], \
        ["Good", "Neutral", "Evil"]]
    W_THRESH = [100, 1150, 3700, 6800, 11000]
    WEAP_TYPE = {
        "Simple Melee": "configs/config_simple_melee.ini", 
        "Simple Ranged": "configs/config_simple_ranged.ini", 
        "Martial Melee": "configs/config_martial_melee.ini", 
        "Martial Ranged": "configs/config_martial_ranged.ini"
    }
    ARM_TYPE = {
        "Light": "configs/config_armor_light.ini", 
        "Medium": "configs/config_armor_medium.ini", 
        "Heavy": "configs/config_armor_heavy.ini"
    }
    
