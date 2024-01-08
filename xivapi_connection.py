import requests
import json
from nicegui import run

class XIVAPIConnection:
    def __init__(self, api_key=""):
        self.api_key = api_key  # not mandatory
        self.base_url = "https://xivapi.com"

    def search_for_item(self, item_name='Iron Ingot'):
        """Searches xivapi for an item and returns the results as a list of dictionaries

        :param item_name: name of item to search for
        :type item_name: str
        :return: returns [{"ID":int,
                            "Icon"=str, # url to icon, e.g. <https://xivapi.com>/i/020000/020601.png
                            "Name":str,
                            "Url":str, # url to item, e.g. <https://xivapi.com>/item/27700
                            "UrlType":str}]
        :rtype: list of dictionaries
        """
        item_name = 'Iron Ingot' if item_name in ('', None) else item_name
        url = self.base_url + "/search?string=" + item_name + "&indexes=Item"
        results = requests.get(url).json()
        return results

    def get_item(self, item_id):

        url = self.base_url + "/item/" + str(item_id)
        results = requests.get(url).json()
        return results

    def get_recipe(self, recipe_id):
        url = self.base_url + "/recipe/" + str(recipe_id)
        results = requests.get(url)
        return results.json()

