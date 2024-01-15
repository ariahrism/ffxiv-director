from datetime import datetime
import dateparser
import requests
import math
from nicegui import ui, run

class UniversalisConnection:
    def __init__(self):
        self.base_url = "https://universalis.app/api/v2/"
        self.datacenters = {}
        self.build_datacenters()
        
    def build_datacenters(self):
        datacenters_list = requests.get("https://universalis.app/api/v2/data-centers").json()
        worldnames_list = requests.get("https://universalis.app/api/v2/worlds").json()

        # Convert worldnames to a dictionary for easy lookup
        worldnames_dict = {world['id']: world['name'] for world in worldnames_list}

        # Merge worlds into datacenters
        for datacenter in datacenters_list:
            datacenter['worlds'] = [{'id': world_id, 'name': worldnames_dict[world_id]} for world_id in datacenter['worlds']]

        # Convert datacenters to a dictionary
        self.datacenters = {datacenter['name']: datacenter for datacenter in datacenters_list}

    def market(self, item_ids, worldDcRegion, numListings=None, historicalListings=None,
                   hq=None, statsWithinDays=None, historicalHours=None, fields=None) -> dict:
            """
            Retrieve market data for the specified item IDs and world, data center, or region.

            Args:
                item_ids (str): The item ID or comma-separated item IDs to retrieve data for.
                worldDcRegion (str): The world, data center, or region to retrieve data for. This may be an ID or a name.
                    Regions should be specified as Japan, Europe, North-America, Oceania, China, or 中国.
                numListings (str, optional): The number of listings to return per item. By default, all listings will be returned.
                historicalListings (str, optional): The number of historical sales to return per item. By default, a maximum of 5 entries will be returned.
                hq (int, optional): Filter for HQ listings and entries. Use 1 for HQ listings and entries, 0 for NQ listings and entries, or omit for both HQ and NQ listings and entries.
                statsWithinDays (str, optional): The time period to calculate stats.
                    By default, this is 7 days.
                historicalHours (str, optional): The time range to collect historical sales.
                fields (str, optional): A comma-separated list of fields that should be included in the response.
                    If omitted, all fields will be returned. For example, if you're only interested in the listings price per unit,
                    you can set this to "listings.pricePerUnit".

            Returns:
                dict: The market data retrieved from the Universalis API.

            """
            url = self.base_url + f"{worldDcRegion}/{item_ids}?"
            if numListings:
                url += f"listings={numListings}&"
            if historicalListings:
                url += f"entries={historicalListings}&"
            if hq:
                url += f"hq={hq}&"
            if statsWithinDays:
                # convert days to milliseconds then add to url
                url += f"statsWithin={statsWithinDays * 24 * 60 * 60 * 1000}&"
            if historicalHours:
                # convert hours to seconds then add to url
                url += f"entriesWithin={historicalHours * 60 * 60}&"
            if fields:
                url += f"fields={fields}"
            print(url)
            try:
                results = requests.get(url).json()
            except:
                ui.notify("Error retrieving market data")
                return None
            return results
        
    async def get_server_prices(self, item_json, market):
        fetched_prices = await run.io_bound(self.market,item_json['ID'], market)
        server_table = {}
        server_by_datacenter = {}
        
        for listing in fetched_prices['listings']:
            #  Create server entry
            if listing['worldName'] not in server_table:
                server_table[listing['worldName']] = {'uploadTime': fetched_prices['worldUploadTimes'][str(listing['worldID'])],
                                                'worldID' : listing['worldID'], 
                                                'listings': []}
            #  Add market listing to appropriate server
            server_table[listing['worldName']]['listings'].append({'hq': listing['hq'], 'quantity': listing['quantity'], 'pricePerUnit': listing['pricePerUnit']})
        server_table = dict(sorted(server_table.items(), key=lambda item: item[1]['uploadTime'], reverse=True))
        
        # Add each server to its datacenter
        for server, details in server_table.items():
            for datacenter in self.datacenters.values():
                if server in [world['name'] for world in datacenter['worlds']]:
                    if datacenter['name'] not in server_by_datacenter:
                        server_by_datacenter[datacenter['name']] = {}
                    server_by_datacenter[datacenter['name']][server] = details
                    break
                
        # Ensure listings are sorted by pricePerUnit and servers are sorted by uploadTime
        for datacenter, servers in server_by_datacenter.items():
            for server, details in servers.items():
                details['listings'] = sorted(details['listings'], key=lambda item: item['pricePerUnit'])
            server_by_datacenter[datacenter] = dict(sorted(servers.items(), key=lambda item: item[1]['uploadTime'], reverse=True))

        return server_table, server_by_datacenter


    def to_epoch(self, dt_string) -> int:
        dt = dateparser.parse(dt_string)
        print(dt)
        # Multiply by 1000 to convert to milliseconds
        epoch = int(dt.timestamp() * 1000)
        return epoch

    def from_epoch(self, epoch) -> str:
        # Divide by 1000 to convert from milliseconds
        dt = datetime.fromtimestamp(epoch / 1000)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def hours_ago(self, epoch=None, timestamp=None):
        if epoch:
            dt = datetime.fromtimestamp(epoch / 1000)
        elif timestamp:
            dt = dateparser.parse(timestamp)
        else:
            raise ValueError("Either epoch or datetime must be provided")
        
        hours_difference = math.ceil((datetime.now() - dt).total_seconds() / 3600)
        return hours_difference




