from nicegui import run

import asyncio
from typing import Optional
import httpx
from nicegui import events, ui

api = httpx.AsyncClient()
running_query: Optional[asyncio.Task] = None


class XIVApiHandler:
    def __init__(self, api_key=""):
        self.api_key = api_key  # not mandatory
        self.base_url = "https://xivapi.com"

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
        results = httpx.get(url).json()
        return results

    def get_recipe(self, recipe_id):
        url = self.base_url + "/recipe/" + str(recipe_id)
        results = httpx.get(url)
        return results.json()
