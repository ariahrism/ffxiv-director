from datetime import datetime
import dateparser
import requests

class UniversalisConnection:
    def __init__(self):
        self.base_url = "https://universalis.app/api/v2/"
        self.datacenters = {}
        self.build_datacenters()
        
    def build_datacenters(self):
        data_center_url = "https://universalis.app/api/v2/data-centers"
        response = requests.get(data_center_url)
        datacenters_list = response.json()

        worlds_url = "https://universalis.app/api/v2/worlds"
        response = requests.get(worlds_url)
        worldnames_list = response.json()

        # Convert worldnames to a dictionary for easy lookup
        worldnames_dict = {world['id']: world['name'] for world in worldnames_list}

        # Iterate over datacenters
        for datacenter in datacenters_list:
            # Replace 'worlds' with a list of dictionaries containing 'id' and 'name'
            datacenter['worlds'] = [{'id': world_id, 'name': worldnames_dict[world_id]} for world_id in datacenter['worlds']]

        # Convert datacenters to a dictionary
        self.datacenters = {datacenter['name']: datacenter for datacenter in datacenters_list}

    def trade_volume(self, item_id=None, worldName=None, dcName=None, fromTime=None, toTime=None):
        url = self.base_url + "extra/stats/trade-volume?"
        if worldName:
            url += f"world={worldName}&"
        if dcName:
            url += f"dcName={dcName}&"
        if item_id:
            url += f"item={item_id}&"
        if fromTime:
            url += f"from={self.to_epoch(fromTime)}&"
        if toTime:
            url += f"to={self.to_epoch(toTime)}"
        results = requests.get(url).json()
        return results

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
            results = requests.get(url).json()
            return results

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
