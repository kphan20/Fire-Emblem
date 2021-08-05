import requests
from bs4 import BeautifulSoup

link_root = 'https://serenesforest.net/'

page = requests.get(link_root)

def get_soup(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, 'lxml')


def get_links(url):
    def is_average_stats(href):
        return 'average-stats' in href
    soup = get_soup(url)
    return [link.get('href') for link in soup.find_all('a', href=is_average_stats)]

#print(get_links('https://serenesforest.net/the-sacred-stones/characters/average-stats/'))
stat_names = ['hp', 'str', 'skl', 'spd', 'lck', 'def_', 'res']
def get_stats(url):
    soup = get_soup(url)
    stats_tr_tag = soup.find_all('tr')[-2]
    stats = stats_tr_tag.find_all('td')[1:]
    stats_dict = {}
    for index, tag in enumerate(stats):
        stats_dict[stat_names[index]] = float(tag.string)
    return stats_dict
print(get_stats('https://serenesforest.net/the-sacred-stones/characters/average-stats/eirika/'))
