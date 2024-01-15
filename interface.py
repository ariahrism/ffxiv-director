from debug_ui import DebugUI, JsonViewer
from nicegui import ui, run, app
from xivapi_connection import XIVApiHandler
from universalis_connection import UniversalisConnection
import asyncio
import time

# Custom CSS variables
# ui.add_head_html('''
#     <style>
#         :root {
#             --nicegui-default-padding: 0.5rem;
#             --nicegui-default-gap: 3rem;
#         }
#     </style>
# ''')

ui.add_head_html('''
<link href='//fonts.googleapis.com/css?family=Open+Sans:400italic,600italic,700italic,400,600,700' rel='stylesheet' type='text/css'>
<style>
    * {
        font-family: "Open Sans", gill sans, sans-serif;
    }
</style>
''')
class BasicContainers:
    def __init__(self):
        # ui.query('.nicegui-content').classes('p-0 gap-0')
        # ui.query('.nicegui-header').classes('p-0')
        # ui.query('body').style('--q-dark-page: #FA00E9;')
        # ui.query('body').style('background-color: var(--q-secondary);')
        # ui.left_drawer.default_style('background-color: var(--q-secondary);')
                
        ui.image.default_props('spinner-size="1rem"')
        # ui.label.default_style('font-family: "Open Sans";')
        ui.add_head_html('<link rel="preload" as="image" href="https://universalis.app/i/game/hq.png" />')
        
        self.page_container = ui.column().classes('w-full gap-0 flex-nowrap min-h-[100lvh] items-stretch')
        with ui.header().props('reveal elevated').classes('min-h-[4.5rem] overflow-y-visible ') as self.header_container:
            self.header = ui.row().classes('p-1.5 -m-1.5 items-end whitespace-nowrap overflow-x-auto overflow-y-visible flex-nowrap')
            
        self.sidebar = ui.left_drawer().props('bordered elevated behavior=mobile')
        self.dark = ui.dark_mode()
        
        with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
            with ui.column().classes('place-items-end') as self.buttons:
                ui.button(icon='menu', on_click=lambda: self.sidebar.toggle()).props('round')
                self.dark_button = ui.button(icon='dark_mode', on_click=self.dark.toggle).props('round')
                
        with self.page_container:
            self.top_pane = ui.row().classes('w-full p-0 gap-0 min-h-[15rem]').style('align-items: stretch;')
            self.bottom_pane = ui.row().classes('relative grow w-full p-0')
                              
            with self.top_pane:
                    self.item_pane = ui.column().classes('grow p-4 min-w-[20rem] min-h-[0rem] min-[900px]:max-w-[20rem]')
                    self.server_pane = ui.row().classes('grow p-0 flex-auto w-[30rem] gap-0')
                        
        with self.sidebar:
            ui.label('Experimenting with colors')
            ui.button('Colors1', on_click=lambda: ui.colors(primary= '#2c3e50', secondary= '#bdc3c7', accent= '#1abc9c', dark= '#34495e', positive= '#2ecc71', negative= '#c0392b', info= '#4682b4', warning= '#f1c40f'))
            ui.button('Colors2', on_click=lambda: ui.colors(primary= '#2C3E50', secondary= '#E67E9D', accent= '#7DCFB6', dark= '#495057', positive= '#F9CA24', negative= '#5B2C6F', info= '#4B77BE', warning= '#FF6B6B'))
            ui.button('Colors3', on_click=lambda: ui.colors(primary= '#3F88C5', secondary= '#6C7A89', accent= '#7FFF00', dark= '#000000', positive= '#FFD700', negative= '#8B0000', info= '#4682B4', warning= '#FF7F50'))


class PageFunctionality:
    def __init__ (self):
        self.xiv = XIVApiHandler()
        self.uv = UniversalisConnection()
        self.popup = ui.dialog()
        self.last_search = 'Iron Ingot'
        with layout.buttons:
            self.search_button = ui.button(icon='search', on_click=self.open_search_modal).props('push round size="20px" color="secondary"').move(0)
        
    
    async def open_search_modal(self):
        #  Popup the search box,  call item_selected() upon selection
        with self.popup:
            self.popup.clear()
            self.search_container = ui.card().classes('p-4 fixed top-6 left-20 gap-2')
        self.popup.open()
        
        with self.search_container:
            self.search_box = ui.input('Search for an item', 
                                placeholder='Iron Ingot',
                                on_change=lambda e: build_results(e.value))\
                                .props('autofocus clearable dense')
            self.search_box.on('keydown.enter', lambda e = self.search_box.value: build_results(e))
            #  TODO: Figure out how to make the input remember the last search
            
            loading = ui.spinner('grid', size='md', color='accent')
            async def build_results(text):
                loading.visible = True
                if not text:
                    text = 'Iron Ingot'
                search_results.clear()
                results = await self.xiv.search(text)
                loading.visible = False
                if not results:
                    return
                with search_results: 
                    for item in results.json()['Results'][:10] or []:  # iterate over the response data
                        with ui.row().on('click', 
                                         lambda r = item:(self.item_selected(r['ID']))
                                        ).classes('items-center'):
                            ui.image(self.xiv.base_url + item['Icon']).classes('w-10')
                            ui.label(item['Name']) 
                
            self.search_box.bind_value(page,'last_search')
            search_results = ui.column()
            await build_results(self.search_box.value)
            loading.visible = False
            
    async def item_selected(self, item_id: int) -> None:
        # Get item data from xivapi and notify other functions to populate the panes
        layout.header.clear()
        self.popup.close()

        with layout.header:
            loading = ui.spinner('facebook', size='md', color='accent')
            item_json = await run.io_bound(self.xiv.get_item, item_id)
            # TODO: handle connection errors
            loading.visible = False

            ui.image(self.xiv.base_url +
                     item_json['Icon']).classes('w-10 min-w-[2.5rem]')
            ui.label(item_json['Name']).classes('text-h4')
            ui.label('iLvl: ' + str(item_json['LevelItem'])).classes('text-subtitle2')

        asyncio.gather(
            self.populate_item_pane(item_json),
            # self.populate_search_history(item_json),
            self.populate_server_pane(item_json),
            self.show_recipe(item_json)
        )
        # jv.set_json(item_json)
               
    async def populate_item_pane(self, item_json): 
        layout.item_pane.clear()      
        with layout.item_pane as container:
            container.classes('border-t-2')
            with ui.column():
                ui.html(item_json['Description']) if item_json['Description'] else None
                with ui.row():
                    ui.label('Craftable: Yes' if 'Recipes' in item_json else 'Craftable: No')
                    price = f'{str(item_json["PriceMid"])} gil' if 'GilShopItem' in item_json['GameContentLinks'] else 'No'
                    ui.label('Sold by Merchant: ' + price)
    
    async def populate_search_history(self, item_json):
        with layout.search_history as container:
            ui.image(self.xiv.base_url + item_json['Icon']).classes('min-w-[3rem] min-h-[3rem]')\
                .on('click', lambda: self.item_selected(item_json['ID'])).move(target_index=0)
                #  TODO: Remove the item from the search history, since a new one will appear at the top
        
    async def populate_server_pane(self, item_json):
        dc = "Japan"
        layout.server_pane.clear()
        with layout.server_pane:
            with ui.column().classes('w-full h-full place-items-center') as loading:
                ui.spinner('cube', size='md', color='accent')
        await asyncio.sleep(0)
        server_prices, datacenter_prices = await self.uv.get_server_prices(item_json, dc)
        
        with layout.server_pane:
            datacenter_tabs = ui.tabs().classes('w-full')
            tab_panels = ui.tab_panels(datacenter_tabs, value='Elemental').classes('w-full bg-inherit p-0').props('swipeable')
        
        with datacenter_tabs:
            for datacenter in datacenter_prices:
                ui.tab(datacenter, label=datacenter)

        panel_style = 'px-2 flex place-items-center flex-row flex-wrap grid grid-cols-2 ' +\
                      'min-[400px]:grid-cols-3 min-[640px]:grid-cols-4 min-[1400px]:grid-cols-8'
        loading.visible = False
        await asyncio.sleep(0.5)
        layout.server_pane.update()
        with tab_panels:
            for datacenter, server_prices in datacenter_prices.items():    
                with ui.tab_panel(datacenter).classes(panel_style):
                    for world_name, details in server_prices.items():
                        with ui.card().classes('min-h-[11rem] w-[7.5rem] items-center gap-2 p-2').style(''):
                            self._build_card_contents(world_name, details)

    def _build_card_contents(self, world_name, details):
        ui.label(world_name).classes('text-sm my-1' if len(world_name) > 11 else 'text-lg')
        
        hours = self.uv.hours_ago(epoch = details['uploadTime'])
        if hours >= 12:
            hours_class = 'text-xs -mt-3 text-red-500'
        elif hours >= 5:
            hours_class = f'text-xs -mt-3 text-amber-{15-hours}00'
        else:
            hours_class = 'text-xs -mt-3'
        ui.label(f'{hours}h ago').classes(hours_class)            
        ui.separator()

        with ui.grid(columns=2).classes('w-[6.0rem] gap-0 px-0 content-end'):
            for listing in details['listings'][:5]:
                
                price_font = 'text-right '
                if listing['pricePerUnit'] >= 10000000:
                    price_font += 'text-[0.5rem]'
                elif listing['pricePerUnit'] >= 1000000:
                    price_font += 'text-[0.6rem]'
                elif listing['pricePerUnit'] >= 100000:
                    price_font += 'text-[0.7rem]'
                else:
                    price_font += 'text-[0.75rem]'

                with ui.row().classes('align-right items-center gap-0 p-0'):
                    base64 = '''data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAABdUlEQV
                    R42mNggAEOBkUGB4ZQhggGXwZTBnEGFgYkwMQgxuBTtufo20+//v+//mnLM99pDNYMfAhpebP6A6//g8GrH9c/Xf
                    /099/mszxODLwQBWJm9a9+gCSPvg1cxRDP4M8QLJM3ZfWxbQzKDMwMQLvcDr0BSXfdBbpAmoEVqIWRgZtBxcNhih
                    0DO1B/8ByQ9JInDN5AYQRgBEpygEzQmXb7//8vv1UaGGQZNBmcGTwYTBhEQRIwYLXpxf//W18wRAjGTLx8/sPNzx
                    ue27cxqCG8abXjJch+7o5LH/9Dwbc/IbMZZGAK9Gbc+/+/8XbHnf9I4OZnBk+YNWLh8///X/QYon/Kff3J2hO67v
                    79517OwAVRwMrgfvzd0++3v/z/v+E5MKCFGYQY/LefjEmBKWBgELdpePH925///zOOMahDTG0PFVdEOJOZQd6g4e
                    bn//+rDjFoAwMeFHic6JElwRlcsebgsQhbVAlkwAEMKFWg/UyowgAZt6pO9HS0MgAAAABJRU5ErkJggg=='''
                    ui.html('<img src="'+base64+'">').classes('ml-3 w-3') if listing['hq'] else None 
                    # ui.image(base64).classes('ml-3 w-3') if listing['hq'] else None 
                    ui.space()
                    ui.label(f' {listing["quantity"]}').classes(price_font)
                ui.label(f'{int(listing["pricePerUnit"]):,}g').classes('ml-2 '+price_font)

    async def show_recipe(self, item_json):

        with layout.bottom_pane as container:
            container.clear()
            with ui.column().classes('w-full h-full place-items-center') as loading:
                ui.spinner('cube', size='md', color='accent')
            tree_data = await self.xiv.build_recipe_tree(item_json.get('Recipes')[0]['ID'], is_root=True)
            await asyncio.sleep(0.5)
            loading.visible = False
            tree = ui.tree([tree_data], 
                           node_key='tID', 
                           label_key='ItemName',
                           children_key='Ingredients',
                           on_select=lambda e: ui.notify(e.value)).expand()
             

layout = BasicContainers()

jv = JsonViewer(layout.buttons)
debug_ui = DebugUI(layout.buttons, [layout.top_pane, layout.bottom_pane, 
                                    layout.header, layout.item_pane, 
                                    layout.server_pane, layout.sidebar])

page = PageFunctionality()

with layout.buttons:
    ui.button('Ingot', on_click=lambda:page.item_selected(5057))
    ui.button('Coatee', on_click=lambda:page.item_selected(11961))

ui.run(show=False, port=8188, title='FFXIV Director',
       favicon='https://xivapi.com/favicon.ico')
