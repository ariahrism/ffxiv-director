from nicegui import run
import requests
import asyncio
from typing import Optional
import httpx
from nicegui import events, ui
import time

api = httpx.AsyncClient()
running_query: Optional[asyncio.Task] = None # Allows task object to be a boolean


class XIVApiHandler:
    def __init__(self, api_key=""):
        self.api_key = api_key  # not mandatory
        self.base_url = "https://xivapi.com"
        self.tID = 0

    async def search(self, value):
        '''Search as you type. Returns json data from xivapi.com.
        :param item_name: name of item to search for
        :type item_name: str
        :return: returns [{ID, Icon, Name, Url, UrlType}]'''
        global running_query
        if value is None or len(value) < 3:
            return
        if running_query:
            running_query.cancel()  # cancel the previous query; happens when you type fast
        # store the http coroutine in a task so we can cancel it later if needed
        running_query = asyncio.create_task(
            api.get(self.base_url + f"/search?string={value}&indexes=Item"))
        response = await running_query
        if response.text == '':
            return
        running_query = None
        return response

    def get_item(self, item_id):
        url = self.base_url + "/item/" + str(item_id)
        results = requests.get(url).json()
        return results

    def get_recipe(self, recipe_id):
        url = self.base_url + "/recipe/" + str(recipe_id)
        results = requests.get(url)
        recipe = results.json()
        print(url, recipe["ItemResult"]["Name"], recipe["ItemResult"]["ID"])
        return recipe
    
    async def build_recipe_tree(self, recipe_id, is_root=False):
        recipe = self.get_recipe(recipe_id)
        
        # If this is the root item, add its details
        if is_root:
            recipe_hierarchy = {
                "tID" : str(self.tID),
                "ItemName": recipe["ItemResult"]["Name"],
                "ItemID": recipe["ItemResult"]["ID"],
                "Icon": recipe.get("Icon", ""),
                'Ingredients':[]
            }
        else:
            recipe_hierarchy = []

        # time.sleep(0.2)
        await asyncio.sleep(0.05)
        
        for i in range(8):
            
            ItemIngredient = f'ItemIngredient{i}'
            AmountIngredient = f'AmountIngredient{i}'
            ItemIngredientRecipe = f'ItemIngredientRecipe{i}'
            
            if ItemIngredient in recipe and recipe[ItemIngredient] is not None:
                self.tID += 1
                ingredient = {
                    "tID" : str(self.tID),
                    "ItemName": f'{recipe[AmountIngredient]}x {recipe[ItemIngredient]["Name"]}',
                    "ItemID": recipe[ItemIngredient]["ID"],
                    "Icon": recipe[ItemIngredient]["Icon"],
                    "Amount": recipe[AmountIngredient],
                }
                
                if ItemIngredientRecipe in recipe and recipe[ItemIngredientRecipe] is not None:
                    ingredient["Ingredients"] = await self.build_recipe_tree(recipe[ItemIngredientRecipe][0]['ID'])


                if not is_root:
                    recipe_hierarchy.append(ingredient)
                else:
                    recipe_hierarchy["Ingredients"].append(ingredient)
        if is_root:
            self.tID = 0
        return recipe_hierarchy


# xiv = XIVApiHandler()
# import pprint
# pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)

# output = xiv.build_recipe_tree(2741, True)

# pp.pprint(output)

# def add_ingredients(ingredient_list):
#     new_list = []
#     for item in ingredient_list if ingredient_list is not None else []:
#         new_list.append({'ItemName':item['ItemName'],
#                          'Amount': item['Amount'],
#                          'Icon':item['Icon'],
#                          'Ingredients': add_ingredients(item.get('Ingredients')) if item.get('Ingredients') is not None else None
#                          })
#     return new_list

# # new_format = {
# #                 'ItemName':output['ItemName'],
# #                 'Icon':output['Icon'],
# #                 'Ingredients': add_ingredients(output.get('Ingredients')) if output.get('Ingredients') is not None else None
# #                 }

# # pp.pprint(new_format)