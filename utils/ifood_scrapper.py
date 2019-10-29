import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

base_url = 'https://www.ifood.com.br/delivery'


def scrapper(state, restaurant):
    url = f"{base_url}/{state}/{restaurant}/"
    req = requests.get(url)

    if req.status_code == 200:
        content = req.content

        soup = BeautifulSoup(content, 'html.parser')

        groups = soup.find_all(name='div', attrs={'class': 'restaurant-menu-group'})
    
        menu = {}
        for group in groups:
            title = group.find(name='h2', attrs={'class': 'restaurant-menu-group__title'})
            dishes = group.find_all(name='a', attrs={'class': 'dish-card'})
            
            dishes_container = []
            for dish in dishes:
                description = dish.find(name='span', attrs={'class': 'dish-card__description'})
                detail = dish.find(name='span', attrs={'class': 'dish-card__details'})
                price = dish.find(name='span', attrs={'class': 'dish-card__price'})
                
                price = re.search('\d+\,\d{1,2}', price.get_text()).group().replace(',', '.')
                price = float(price)

                dishes_container.append({
                    'description': description.get_text(), 
                    'detail': detail.get_text(), 
                    'price': price})

                menu.update({ title.get_text(): dishes_container })
        return menu
    else:
        return 'something bad happened.'
    
