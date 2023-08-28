#!/usr/bin/python

# imports
from configparser import ConfigParser
from copy import deepcopy as dc
from dnd_world import World, args_active, gradio_ui_elements
import ran_gen
import random
import die
import json
from markdown.extensions.tables import TableExtension
from markdown import markdown
from textwrap import wrap

# functions
def stat_gen(): 
    "Roll 4d6, drop the lowest, return total sum"
    
    rolls = [die.rolld(6), die.rolld(6), die.rolld(6), die.rolld(6)]
    rolls.remove(min(rolls))
            
    return sum(rolls)

def get_alig(alig_list):
    """
        First   [0] is lawful, neutral, chaotic
        Second  [1] is good, neutral, evil
    """
    if alig_list[0] == 2 and alig_list[1] == 2:
        return "True Neutral"
    
    al_li = []
    for i in range(len(alig_list)):
        al_li.append(World.ALIG_CHART.value[i][alig_list[i]-1])
    
    return f"{al_li[0]} {al_li[1]}"

def get_class_ster_nums(cl, data, md, cv):
    """
        cl = class;data = data value to search
        md = mod (how many # per list); cv = should convert to int
    """
    config = ConfigParser()
    config.read("configs/config_races.ini")
    li = []
    li_s = config[cl][data].split(",")
    pos = 0
    
    if cv:
        if md == 1:
            while pos < len(li_s):
                li.append(int(li_s[pos]))
                pos += md
        else:
            while pos < len(li_s):
                li.append([int(li_s[pos]), int(li_s[pos+1])])
                pos += md
        
        return li
    else:
        return li_s

# body
class character:
    
    def __init__(self):
        # character traits
        self.race      = ran_gen.rrace()
        self.player = {'name': args_active['player_name'] }
        self.p_class     = ran_gen.rclass()
        self.p_alig_val  = [die.rolld(3), die.rolld(3)]
        self.p_alignment = get_alig(self.p_alig_val)
        
        # attributes
        self.p_age       = self.smart_age()
        self.p_fname     = ran_gen.rname(self.race.name, "First")
        self.p_lname     = ran_gen.rname(self.race.name, "Last")
        self.name      = self.p_fname + " " + self.p_lname
        
        # financial & vanity
        self.p_net_worth = ran_gen.rwealth()
        self.p_wea_desc  = ran_gen.get_wealth_desc(self.p_net_worth)
        self.p_clothing  = ran_gen.rarmor()
        self.p_weapon    = ran_gen.rweapon()
        
        # stats
        self.str = stat_gen()
        self.dex = stat_gen()
        self.con = stat_gen()
        self.wis = stat_gen()
        self.int = stat_gen()
        self.cha = stat_gen()
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    def toMarkdown(self):
        formatted = self.format_desc()
        stats = formatted[0]
        weapon = formatted[1]
        
        return_string = '''
        # {s.p_fname}

        This person is  {s.race.name} {s.p_class} whose name is {s.name}.
        {s.p_fname} is {s.p_alignment}, {s.p_age} years old, and has a net worth of {s.p_net_worth}

        {s.p_fname} is wearing {s.p_clothing}, and {s.p_wea_desc}. 
        {s.p_fname} is wielding .
        '''.format(s=self)
        return return_string
    def format_desc(self):
        "Extra formatting for descriptions"
        stats = [self.str, self.dex, self.con, self.wis, self.int, self.cha]
        form = []
        ind = "                       "
        
        for stat in stats:
            if stat < 10:
                form.append(str(stat).rjust(2, ' '))
            else:
                form.append(stat)
                
        res = f" {ind}|     STR {form[0]}     WIS {form[3]}     |" \
            f"\n {ind}|     DEX {form[1]}     INT {form[4]}     |" \
            f"\n {ind}|     CON {form[2]}     CHA {form[5]}     |"
        
        if self.race.name == "Elf": grammar = "an"
        else: grammar = "a"
        
        if "Dart" in self.p_weapon:
            weapon = "a handful of darts"
        else: weapon = "a " + self.p_weapon
        
        return [res, weapon, grammar]
    def print_desc(self):
        "Display a brief, cleanly-formatted description of generated character"
        
        formatted = self.format_desc()
        stats = formatted[0]
        weapon = formatted[1]
        return_list = []
        char_id = f"This person is {formatted[2]} {self.race.name} {self.p_class} " \
            f"whose name is {self.name}."
        desc = f"{self.p_fname} is {self.p_alignment}, {self.p_age} years old, and " \
            "has a net worth of {:,d} GP.".format(self.p_net_worth)
        breaker = "".center(80, '-')
        appearance = f"{self.p_fname} is wearing {self.p_clothing}, and {self.p_wea_desc}"
        armed = f"{self.p_fname} is wielding {weapon}."
        desc_dict = {
            "   Description: ": desc,
            "   Appearance : ": appearance,
            "   Wielding   : ": armed
        }
        
        return_list.append("\n\n\n" + char_id.center(80, ' '))
        return_list.append(f"{breaker}\n{stats}\n{breaker}\n")
        for key, val in desc_dict.items():
            wrapped = wrap(f"{key}{val}", 77)
            return_list.append(wrapped[0])
            if len(wrapped) > 0:
                for i in range(len(wrapped)-1):
                    return_list.append("".ljust(len(key), ' ') + wrapped[i+1])
            return_list[-1] += "\n"
        
        return_string = ""
        for line in return_list:
            return_string += (line + "\n")
        return(return_string)
    def logical_stereotype(self, *r):
        """Normalize stereotypical alignment & class based on 5th ed. PHB"""
        if len(r) > 0: self.race.name = r[0]
        if self.race.name != "Human":
            pot_aligns = get_class_ster_nums(self.race.name, "pot_aligns", 1, \
                        True)
            pot_alig_nums = get_class_ster_nums(self.race.name, "pot_alig_nums", \
                        2, True)
            class_nums = get_class_ster_nums(self.race.name, "class_nums", 1, \
                        True)
            pot_classes = get_class_ster_nums(self.race.name, "pot_classes", 1, \
                        False)
            
            ster_align = die.rolld(100)    # sterotypical alignment %
            ster_class = die.rolld(100)    # stereotypical class %
                
            for i in range(len(pot_aligns)):
                if ster_align <= pot_aligns[i]:
                    self.p_alig_val[0] = pot_alig_nums[i][0]
                    self.p_alig_val[1] = pot_alig_nums[i][1]
                    
                    for j in range(len(class_nums)):
                        if ster_class <= class_nums[j]:
                            self.p_class = pot_classes[j]
                            break
                    break
    
        self.p_alignment = get_alig(self.p_alig_val)
        
        
            
    def smart_age(self):
        """
            Give character an appropriate age for given race
            Max age taken from 5th edition PHB, or D&D Beyond if not
            listed in PHB
        """
        r = die.rolld(100) # random percentage
        r_a_mod = random.randrange(86, 99) / 100 # age modifier
        
        # the following are ordered according to dnd_world
        maxa = [433, 845, 167, 98, 94, 522, 222, 80, 102] # max ages
        aa = [17, 17, 17, 17, 15, 20, 17, 16, 17] # adulthood ages
        r_a_check = [.74, .88, .85, .85, .70, .82, .88, .79, .82] # age check
        alter_chance = [89, 89, 89, 89, 85, 89, 89, 82, 89] # age alter chance
        age = 1
        for i in range(len(World.RACES.value)):
            if self.race.name == World.RACES.value[i]:
                age = die.rolld(maxa[i] - aa[i]) + aa[i]
                if age >= int(r_a_check[i] * maxa[i]) and r < alter_chance[i]:
                    age = int(age * r_a_mod)
                break
        
        return age
   
    def smart_wealth(self):
        "Make a somewhat logical attempt at calculating wealth"
        w_brackets = [9.2, 50, 98.2, 99.6, 100]
        w_mod = [1.08, 1.02, 1.01, 1.00, 1.02, 1.08, 1.02, .98, 1.03]
        
        p = round(random.uniform(0, 100), 2)
        rich_luck = random.uniform(0, 100)
        rl_mod = round(random.uniform(1.2, 2), 2)
        new_wealth = 0
        
        for i in range(len(w_brackets)):
            if p <= w_brackets[i]:
                if w_brackets[i] == w_brackets[0]:
                    new_wealth = random.randint(1, \
                        World.W_THRESH.value[i])
                    break
                else:
                    new_wealth = random.randint( \
                        World.W_THRESH.value[i-1], \
                        World.W_THRESH.value[i])
                    if w_brackets[i] == w_brackets[-1] and rich_luck > 90:
                        new_wealth = int(new_wealth * rl_mod)
                    break
            
        for i in range(len(World.RACES.value)):
            if self.race.name == World.RACES.value[i]:
                new_weath = int(new_wealth * w_mod[i])
                break
        
        self.p_net_worth = new_wealth
        self.p_wea_desc = ran_gen.get_wealth_desc(new_wealth)

    def smart_stats(self):
        config = ConfigParser()
        ph = [self.str, self.dex, self.con, self.wis, self.int, self.cha]
        ph.sort()
        ph.reverse()
        p = random.randint(1, 100)
        thresh = []
        to_read = ""
        
        for i in range(len(World.CLASSES.value)):
            if self.p_class == World.CLASSES.value[i]:
                to_read = f"configs/config_{World.CL_SH.value[i]}.ini"
                break
            
        config.read(to_read)
        
        for section in config.sections():
            thresh.append(int(section))
        
        for i in range(len(thresh)):
            if p <= thresh[i]:
                for st_name, st_pos in config[str(thresh[i])].items():
                    setattr(self, st_name, ph[int(st_pos)])
                break
            
    def smart_gear(self):
        conf_class = ConfigParser()
        conf_class.read("configs/config_classes.ini")
        conf_armor = ConfigParser()
        conf_weap = ConfigParser()
        
        c = self.p_class
        
        arm_budget = int(self.p_net_worth * .38)
        weap_budget = int(self.p_net_worth * .1)
        shield_budg = int(self.p_net_worth * .08)
        shield_chan = random.randint(1, 100)
        can_wield_shield = True
        
        avail_armor = []
        avail_weap = []
        
        if conf_class[c]["ar_kind"].split(",")[0] != '':
            armor_type = random.choice(conf_class[c]["ar_kind"].split(","))
        else:
            armor_type = random.choice(list(World.ARM_TYPE.value.keys()))
            
        conf_armor.read(World.ARM_TYPE.value[armor_type])
        
        for section in conf_armor.sections():
            avail_armor.append(dc(section))
            
        for _ in range(len(avail_armor) + 1):
            if len(avail_armor) == 0:
                armor = "slightly-tattered clothing"
                break
            
            pick = random.choice(avail_armor)
            price = int(conf_armor[pick]["price"])

            if price <= arm_budget:
                armor = pick
                break
            else:
                avail_armor.remove(pick)
        
        weap_type = random.choice(conf_class[c]["weap_type"].split(","))
        conf_weap.read(World.WEAP_TYPE.value[weap_type])
        
        for sect in conf_weap.sections():
            avail_weap.append(dc(sect))
        
        for _ in range(len(avail_weap) + 1):
            if len(avail_weap) == 0:
                weapon = "pair of bare hands"
                break
            
            pick = random.choice(avail_weap)
            price = float(conf_weap[pick]["price"])
            
            if price <= weap_budget:
                weapon = pick
                break
            else:
                avail_weap.remove(pick)
                
        shield_conditions = [
            conf_class[c]["shield"] == "True", \
            shield_budg >= 10, \
            shield_chan <= 40, \
            conf_weap[pick]["can_wield_shield"] == "True"]
        
        for cond in shield_conditions:
            if not cond:
                can_wield_shield = False
                break
            
        if can_wield_shield:
            weapon += " and shield"
        
        self.p_clothing = armor
        self.p_weapon = weapon
