#!/usr/bin/python

# imports
from dnd_char import character
from dnd_world import World, all_races, gradio_ui_elements, args_active, populate_possible_races
from time import sleep
import argparse
import json
import gradio as gr

# functions
def clear(): print('\033[H\033[J', end="")
def beautify(s): print(f"\n\n{s}\n\n")
def alert(s): beautify(f"       {s}")
def req_input(): return int(input())

def menu():
    "Display menu options"
    print(" 1| Generate New Logical Character")
    print(" 2| Generate New Random Character")
    print(" 3| Generate Character Of Certain Race")
    print("-----------------------------------")
    print(" 8| Save Character To File")
    print(" 9| Print Stats of Current Character")
    print("-1| Exit Program")
    print("-----------------------------------")
    
def display_races():
    "Display races in D&D"
    r_ph = "\n\n"
    for i in range(len(World.RACES.value)):
        r_ph += f"   {i+1}| {World.RACES.value[i]}\n"
    print(f"{r_ph}\n")
    
def display_classes():
    "Display classes in D&D"
    c_ph = "\n\n"
    for i in range(len(World.CLASSES.value)):
        c_ph += f"   {i+1}| {World.CLASSES.value[i]}\n"
    print(f"{c_ph}\n")

def prompt(s):
    print(s, end="")
    return req_input()
    
def save_char(c, char_made, has_saved):
    "Save character to text file"
    
    if char_made == False:
        alert("ERROR: Generate character before saving.")
    elif has_saved == True:
        alert("ERROR: Character has already been saved.")
        return True
    else: 
        file_name = f"{c.race.name} {c.p_class} - {c.name}.txt"
        json_file_name = f"{c.race.name} {c.p_class} - {c.name}.json"
        json_save_path = f"./characters/{json_file_name}"
        savepath  = "./characters/" + file_name
        current   = "./current_character.txt"
        files     = [savepath, current]
        
        file = open(json_save_path, 'w')
        file.write(c.toJSON())
        file.close()

        for a_file in files:
            file = open(a_file, 'w')
            file.write(c.print_desc())
            file.close()
        
        alert(f"'{file_name}' saved in characters folder")
        
        return True
    
def make_log_character(*r):
    "Generate character based on 5e PHB logic"
    new = character()
    if len(r) > 0: new.logical_stereotype(r[0])
    else: new.logical_stereotype()
    new.smart_stats()
    new.smart_wealth()
    new.smart_gear()
    
    print("- - - - GENERATED LOGICAL CHARACTER - - - -".center(80, ' '))
    print(f"{new.print_desc()}\n")
    
    return new

def make_ran_character():
    "Generate character randomly"
    new = character()
    print("- - - - GENERATED RANDOM CHARACTER - - - -".center(80, ' '))
    print(f"{new.print_desc()}\n")
    return new.toMarkdown(),new.toJSON()





def parse_arguments():
    parser = argparse.ArgumentParser(description='DnD 5e Character Generator')
    parser.add_argument("--gradio", action='store_true',
                        help='Use this flag to run a gradio interface')
    parser.add_argument("--bind_port", default=8000,
                        help='Which port to run on')
    parser.add_argument("--player_name", default='New Player',
                        help='What player the character is for')
    return parser.parse_args()
parse_arguments()
args_cmdline = parse_arguments()
args_active.update({"gradio": args_cmdline.gradio})
args_active.update({"bind_port": args_cmdline.bind_port})
args_active.update({"player_name": args_cmdline.player_name})

populate_possible_races()
race_choices = [o.name for o in args_active['possible_races']]

print(race_choices)
if args_active['gradio']:
    with gr.Blocks(analytics_enabled=False) as grBlock:
        gr_qa = gr.State([])
        gr.Markdown(
            """
            # DnD 5e Character Generator

            An opinionated character generator which aims to utilize standard data apis to persist DnD characters.

            Output files should be convertable via pandoc into html. The data model of a character should be able to be imagemagick'd into a printable character sheet, and flexible enough to allow for other designs or templates.

            """)
        with gr.Tab("Chat"):
            with gr.Row():
                gradio_ui_elements['selected_race'] = gr.Dropdown(label='Selected race',choices=race_choices)
                gradio_ui_elements['button_generate_random'] = gr.Button('Generate Random')
                gradio_ui_elements['character_markdown'] = gr.Markdown(label="Character as JSON")
                gradio_ui_elements['character_json'] = gr.Textbox(label="Character as JSON")
        with gr.Tab("Settings"):
            with gr.Row():
                gradio_ui_elements['bind_port'] = gr.Textbox(label="The port to bind to",value=args_active['bind_port'])
                gradio_ui_elements['player_name'] = gr.Textbox(label="The player name for the character",value=args_active['player_name'])
                

        gradio_ui_elements['button_generate_random'].click(fn=make_ran_character, inputs=[], outputs=[gradio_ui_elements['character_markdown'],gradio_ui_elements['character_json']])
        gradio_ui_elements['player_name'].change(lambda x: args_active.update({"player_name": x}), gradio_ui_elements['player_name'], None)
        gradio_ui_elements['selected_race'].change(lambda x: args_active.update({"selected_race": x}), gradio_ui_elements['selected_race'], None)
        # gradio_ui_elements['instruct_prompt_template'].change(lambda x: params.update({"instruct_prompt_template": x}), gradio_ui_elements['instruct_prompt_template'], None)
        

    grBlock.queue(concurrency_count=25).launch(server_port=args_active['bind_port'])   
else:
    # body
    clear()
    cont = 1
    has_saved = False
    char_made = False
    debug_count = 500
    curr = character()

    while cont >= 0:
        cont = prompt("Enter a number (0 for menu): ")
        clear()
        
        if cont == 1:
            "Make logical char, display stats, and reset saved stat"
            curr = make_log_character()
            has_saved = False
            char_made = True
            
        elif cont == 2: 
            "Make random char, display stats, and reset saved stat"
            curr = make_ran_character()
            has_saved = False
            char_made = True
            
        elif cont == 3: 
            "Make char with a given race"
            display_races()
            selected_race = prompt("Choose a race: ")
            if selected_race == 0:
                clear()
                pass
            else:
                clear()
                curr = make_log_character(World.RACES.value[selected_race-1])
            
        elif cont == 8: 
            "Display errors w/ saving"
            has_saved = save_char(curr, char_made, has_saved)
            
        elif cont == 9:
            "Print stats if character has been generated"
            if char_made == False:
                alert("ERROR: Generate character before attempting to view their stats.")
            else:
                print(f"{curr.print_desc()}\n")
                
        elif cont == 111:
            for i in range(debug_count):
                print(f"DEBUG MODE (LOG) ({i} of {debug_count})".center(80, '-'))
                curr = make_log_character()
                sleep(.01)
                clear()
            has_saved = False
            char_made = True
            alert("CHAR GEN SUCCESSFUL - NO BUGS")
                
        elif cont == 222:
            for i in range(debug_count):
                print(f"DEBUG MODE (RAN) ({i} of {debug_count})".center(80, '-'))
                curr = make_ran_character()
                sleep(.01)
                clear()
            has_saved = False
            char_made = True
            alert("CHAR GEN SUCCESSFUL - NO BUGS")
            
        elif cont == 0:
            menu()

    clear()
