import requests
from bs4 import BeautifulSoup
import json
from utils import stat_names, complete_stat_names
import os

dirname = os.path.dirname(__file__)


link_root = 'https://serenesforest.net/'

page = requests.get(link_root)

def get_soup(url):
    """Creates BeautifulSoup object from url

    Args:
        url (str): Page url

    Returns:
        BeautifulSoup: BeautifulSoup rendition of page
    """
    page = requests.get(url)
    return BeautifulSoup(page.content, 'lxml')

def parse_try_except(parseFunc, value):
    """Generic function handling parsing of strings

    Args:
        parseFunc (type): Function that produces desired form of string (eg int, float)
        value (str): String to be parsed

    Returns:
        str: Either the parsed string or the original string
    """
    try:
        return parseFunc(value)
    except:
        return value
    
def fill_dict(index_arr, enumerated_list, parser):
    """Fills a dictionary with values from a list of bs4 elements

    Args:
        index_arr (list[str]): List containing the keys of the dictionary
        enumerated_list (list[bs4.element.tag]): List containing table data
        parser (type): Parser class for data elements

    Returns:
        dict: Key-value pairs from "merging" the input lists
    """
    results = {}
    for index, item in enumerated_list:
        results[index_arr[index]] = parse_try_except(parser, item.string)
    return results
    
# For character stats

def get_class_stats(url):
    """Extracts information from the page containing all the classes' base stats

    Args:
        url (str): Url of page containing all the base stats

    Returns:
        dict: Character name-base stat key-value pairs
    """
    classes = {}
    soup = get_soup(url)
    data = soup.find_all('tr')
    for row in data:
        columns = row.find_all('td')
        if columns:
            class_name = columns[0].string
            mov = columns[-3].string
            con = columns[-2].string
            classes[class_name] = {'mov': mov, 'con': con}
            weapon_rank_col = columns[-1].find_all('img')
            if weapon_rank_col:
                conversion = {
                    'E': 0,
                    'D': 1,
                    'C': 2,
                    'B': 3,
                    'A': 4,
                    'S': 5
                }
                weapons = {}
                for rank in weapon_rank_col:
                    weapons[rank['alt']] = conversion[rank.next_element.strip().replace(',', '')]
                classes[class_name]['weapons'] = weapons
    with open(os.path.join(dirname, '../test_files/test10.json') , 'w') as f:
        json.dump(classes, f)
    return classes
#get_class_stats('https://serenesforest.net/the-sacred-stones/classes/base-stats/')

def fe8_class_process(result):
    """Processes dictionary from get_class to control inconsistency in info pages

    Args:
        result (dict): Result dict from get_class method

    Returns:
        dict: Processed dictionary
    """
    myrmidon = {'Joshua': ' (M)', 'Marisa': ' (F)'}
    # prolly make it more specific
    for name in result.keys():
        classname = result[name]['class']
        if classname == 'Lord':
            classname = classname + f' ({name})'
        elif classname in {'Cavalier', 'Paladin', 'Knight', 'Sniper', 'Mercenary', 'Sage', 'Wyvern Rider',
                           'Great Knight', 'Shaman', 'Hero', 'Bishop', 'Wyvern Lord', 'Ranger', 'General', 'Wyvern Knight'}:
            classname = classname + ' (M)'
        elif classname == 'Myrmidon':
            classname = classname + myrmidon[name]
        elif classname in ['Archer', 'Mage', 'Manakete', 'Swordmaster', 'Mage Knight']:
            classname = classname + ' (F)'
        elif classname == 'Mage':
            classname = classname + ' (F)'
        elif classname in ['Journeyman', 'Pupil', 'Recruit']:
            classname = classname + ' (1)'
        result[name]['class'] = classname
    return result

#This method can potentially combine with get_class_stats to get true weapon ranks
def get_class(url, isFe8):
    """Retrieves data from page containing all of the character's base stats

    Args:
        url (str): Url of page
        isFe8 (bool): Used to denote which game info is being scraped for

    Returns:
        dict: [description]
    """
    #'https://serenesforest.net/the-sacred-stones/characters/base-stats/'
    soup = get_soup(url)
    rows = soup.find_all('tr')
    results = {}
    for row in rows:
        character_data = row.find_all('td')
        if character_data:
            name = character_data[0].string.strip().replace('’', "'")
            starting_level = parse_try_except(int, character_data[1].string)
            classname = character_data[2].string.strip()
            # these changes are only applicable to fe8
            # transition to post process function later
            starting_stats = fill_dict(complete_stat_names, enumerate(character_data[3:12]), int)
            affinity = character_data[-1 if isFe8 else -2].img['alt']
            results[name] = {"class": classname, "affinity": affinity, "starting_level": starting_level, "base": starting_stats}
    with open(os.path.join(dirname, '../test_files/test4.json') , 'w') as f:
        json.dump(results, f)
    return results
#get_class('https://serenesforest.net/the-sacred-stones/characters/base-stats/', True)

def get_supports(url):
    """Retrieves supports for each character

    Args:
        url (str): Page url

    Returns:
        dict: Character-support characters key-value pairs
    """
    soup = get_soup(url)
    rows = soup.find_all('tr')
    results = {}
    for row in rows:
        character_data = row.find_all('td')
        if character_data:
            character_name = character_data[0].contents[0].strip().replace('’', "'")
            character_data = character_data[1:]
            support_characters = {}
            for character in character_data:
                content = character.contents
                name = content[0].strip().replace('’', "'")
                base = content[-1].strip()
                if name == base:
                    continue
                support_characters[name] = base
            results[character_name] = support_characters
    return results

#unsure about how to deal with weapon rank gains
def get_promotion_gains(url):
    """Retrieves the stat gains from each promotion

    Args:
        url (str): Page url

    Returns:
        dict: Start class-promotion gains key-value pairs
    """
    soup = get_soup(url)
    rows = soup.find_all('tr')
    results = {}
    for row in rows:
        data = row.find_all('td')
        if data:
            starting_class = data[0].string
            promotion_class = data[1].string
            if starting_class in ['Journeyman', 'Pupil', 'Recruit']:
                starting_class = starting_class + ' (1)'
            
            stats = fill_dict(complete_stat_names, enumerate(data[2:10]), int)
            if results.get(starting_class):
                results[starting_class][promotion_class] = stats
            else:
                results[starting_class] = {promotion_class: stats}
    with open(os.path.join(dirname,'../test_files/test2.json') , 'w') as f:
        json.dump(results, f)
    return results
#get_promotion_gains('https://serenesforest.net/the-sacred-stones/classes/promotion-gains/')

def get_growth_rates(url):
    """Retrieves growth rates for each character

    Args:
        url (str): Page url

    Returns:
        dict: Character-growth rate percentage key-value pairs
    """
    #'https://serenesforest.net/the-sacred-stones/characters/growth-rates/'
    soup = get_soup(url)
    rows = soup.find_all('tr')
    results = {}
    for row in rows:
        data = row.find_all('td')
        if data:
            name = data[0].string
            growths = {}
            for index, stat in enumerate(data[1:]):
                growths[stat_names[index]] = parse_try_except(int, stat.string)
            results[name] = growths
    return results

def handle_recruit_promotions(results, classes):
    """Processes promotions for trainee classes

    Args:
        results (dict): Dictionary containing character data
        classes (dict): Dictionary containing promotion data
    """
    results['Ross']['promotions']['Fighter']['promotions'] = classes['Fighter']
    results['Ross']['promotions']['Pirate']['promotions'] = classes['Pirate']
    results['Ross']['promotions']['Journeyman (2)']['promotions'] = classes['Journeyman (2)']
    results['Amelia']['promotions']['Cavalier (F)']['promotions'] = classes['Cavalier (F)']
    results['Amelia']['promotions']['Knight (F)']['promotions'] = classes['Knight (F)']
    results['Amelia']['promotions']['Recruit (2)']['promotions'] = classes['Recruit (2)']
    results['Ewan']['promotions']['Mage (M)']['promotions'] = classes['Mage (M)']
    results['Ewan']['promotions']['Shaman (M)']['promotions'] = classes['Shaman']
    results['Ewan']['promotions']['Pupil (2)']['promotions'] = classes['Pupil (2)']
    
def create_character_data():
    """Creates master document with information for each character
    """
    results = fe8_class_process(get_class('https://serenesforest.net/the-sacred-stones/characters/base-stats/', True))
    names = results.keys()
    supports = get_supports('https://serenesforest.net/the-sacred-stones/characters/supports/')
    growths = get_growth_rates('https://serenesforest.net/the-sacred-stones/characters/growth-rates/')
    classes = get_promotion_gains('https://serenesforest.net/the-sacred-stones/classes/promotion-gains/')
    valid_class_weapons = get_class_stats('https://serenesforest.net/the-sacred-stones/classes/base-stats/')
    for class_name in classes.keys():
        promotions = classes[class_name].keys()
        for promotion in promotions:
            try:
                if valid_class_weapons[promotion]['weapons']:
                    classes[class_name][promotion].update(valid_class_weapons[promotion]['weapons'])
            except KeyError:
                if valid_class_weapons[promotion + ' (M)']['weapons']:
                    classes[class_name][promotion]['weapons'] = valid_class_weapons[promotion + ' (M)']['weapons']
    for name in names:
        if supports.get(name):
            results[name]['supports'] = supports[name]
        if growths.get(name):
            results[name]['growths'] = growths[name]
        if classes.get(results[name]['class']):
            # add recruit promotions in post processing
            results[name]['promotions'] = classes[results[name]['class']]
        if valid_class_weapons.get(results[name]['class']):
            if valid_class_weapons[results[name]['class']].get('weapons'):
                results[name]['base']['weapons'] = valid_class_weapons[results[name]['class']]['weapons']
        else:
            print(results[name]['class'])
    handle_recruit_promotions(results, classes)
    with open(os.path.join(dirname, '../test_files/test.json'), 'w') as f:
        json.dump(results, f)
create_character_data()

# For items
def get_inventory_links(url):
    """Retrieves links for each type of item/weapon

    Args:
        url (str): Page url

    Returns:
        list[str]: Compilation of the links
    """
    soup = get_soup(url)
    inventory = soup.find('span', string='Inventory').find_next_sibling('ul')
    return [link['href'] for link in inventory.find_all('a')]

weapon_stats = ['name', 'rank', 'range', 'weight', 'might', 'hit', 'crit', 'uses', 'weapon_exp', 'price', 'effects']
def get_weapon_info(url):
    """Retrieves information about all the weapons on a page

    Args:
        url (str): Page url

    Returns:
        Dict: Weapon type-all weapons under that archetype key-value pairs
    """
    soup = get_soup(url)
    weapon_rows = soup.find_all('tr')[1:]
    results = {}
    weapon_type = {}
    for weapon in weapon_rows:
        data = weapon.find_all('td')[1:]
        info = fill_dict(weapon_stats, enumerate(data), float)
        weapon_type[data[0].string] = info
    results[url.split('/')[-2]] = weapon_type
    return results
# results = {}
# for url in get_inventory_links('https://serenesforest.net/the-sacred-stones/')[:-1]:
#     results.update(get_weapon_info(link_root + url))
# with open(os.path.join(dirname, 'tes2t.json'), 'w') as f:
#     json.dump(results, f)
# For class info
FUN_CONSTANT = 100
columns = ['foot', 'armor', 'knight1', 'knight2', 'horse1', 'horse2', 'fighter', 'mage', 'flier', 'bandit', 'pirate']
def get_terrain_info(url):
    """Retrieves all terrain data

    Args:
        url (str): Page url

    Returns:
        dict: Contains terrain stat gains and terrain costs for each class
    """
    soup = get_soup(url)
    terrain_rows = soup.find_all('tr')[2:]
    terrain_stats = {}
    terrain_costs = {}
    for row in terrain_rows:
        cells = row.find_all('td')
        terrain_name = cells[0].string
        terrain_info = {}
        terrain_info['avoid'] = parse_try_except(int, cells[1].string)
        terrain_info['def'] = parse_try_except(int, cells[2].string)
        terrain_info['notes'] = parse_try_except(int, cells[3].string)
        terrain_stats[terrain_name] = terrain_info
        cells = cells[4:]
        for index, class_data in enumerate(cells):
            move_cost = parse_try_except(int, class_data.string)
            movement_class = columns[index]
            if move_cost == "\u2013":
                move_cost = FUN_CONSTANT
            if terrain_costs.get(movement_class):
                terrain_costs[movement_class][terrain_name] = move_cost
            else:
                terrain_costs[movement_class] = {terrain_name: move_cost}
    return {'terrain stats': terrain_stats, 'terrain costs': terrain_costs}

# with open('test.json', 'w') as f:
#     json.dump(get_weapon_info('https://serenesforest.net/the-sacred-stones/inventory/swords/'), f)
#     json.dump(get_terrain_info('https://serenesforest.net/the-sacred-stones/classes/terrain-data/'), f)
# def get_stat_links(url):
#     """Gets links for each character's stat page

#     Args:
#         url (str): Page url containing all character stat pages
#     """
#     def is_average_stats(href):
#         return 'average-stats' in href
#     soup = get_soup(url)
#     return [link.get('href') for link in soup.find_all('a', href=is_average_stats)]
# def get_average_stats(url):
#     """[summary]

#     Args:
#         url ([type]): [description]

#     Returns:
#         [type]: [description]
#     """
#     soup = get_soup(url)
#     stats_tr_tag = soup.find_all('tr')[-2]
#     stats = stats_tr_tag.find_all('td')[1:]
#     stats_dict = {}
#     for index, tag in enumerate(stats):
#         stats_dict[stat_names[index]] = float(tag.string)
#     return stats_dict
# def handle_promotion_stats(soup):
#     entry = soup.find('div', class_="entry")
#     print(entry)
#handle_promotion_stats(get_soup('https://serenesforest.net/the-sacred-stones/characters/average-stats/ross/'))