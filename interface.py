from debug_ui import DebugUI
from nicegui import ui, run
from xivapi_connection import XIVApiHandler
from universalis_connection import UniversalisConnection

class BasicContainers:
    def __init__(self):
        ui.query('.nicegui-content').classes('p-0 gap-0')
        ui.button.default_style('flex-shrink:0;')
        ui.label.default_style('font-family: "Open Sans";')
        self.page_container = ui.row().classes('w-full gap-0 flex-nowrap min-h-[100svh] items-stretch')

        with self.page_container:
            #  TODO: consider different layout for mobile phones
            #  TODO: consider adding hamburger menu for accessing other pages
            
            self.sidebar = ui.column().classes('fixed top-0 p-4 items-center overflow-hidden min-h-[100svh] w-[5.5rem]') 
            self.main_pane = ui.column().classes('ml-[5.5rem] grow p-0 justify-center items-center gap-0 overflow-y-auto') 
            
            with self.sidebar:
                self.search_button = ui.button(icon='search', on_click=page.search_clicked)\
                                        .classes('fixed top-4 min-h-[3.5rem] z-10')
                self.search_history = ui.column().classes('mt-[2.6rem] pt-[2rem] items-center max-h-[90svh] grow p-0 overflow-y-auto')\
                    .style('mask-image: linear-gradient(to bottom, transparent 0%, black 30px, black calc(100% - 80px), transparent 100%); scrollbar-width: none;')

            with self.main_pane:
                self.header = ui.row().classes('w-full min-h-[3.5rem] items-end p-4 whitespace-nowrap overflow-x-auto flex-nowrap')
                self.top_pane = ui.row().classes('w-full p-0 gap-0 min-h-[15rem]').style('align-items: stretch;')
                self.bottom_pane = ui.row().classes('relative grow w-full p-4')
                
                with self.top_pane:
                    self.item_pane = ui.column().classes('grow p-4 min-w-[20rem] min-h-[15rem] min-[650px]:max-w-[20rem]')
                    self.server_pane = ui.row().classes('grow p-4 flex-auto w-[15rem] gap-4')

class PageFunctionality:
    def __init__ (self, page_name):
        self.xiv = XIVApiHandler()
        self.uc = UniversalisConnection()
        self.popup = ui.dialog()
        self.last_search = 'Iron Ingot'

    
    async def search_clicked(self):
        with self.popup:
            self.popup.clear()
            self.search_container = ui.column().classes('p-4 bg-slate-100 fixed top-6 left-20 gap-2')
        self.popup.open()
        
        with self.search_container:
            self.search_box = ui.input('Search for an item', 
                                placeholder='Iron Ingot',
                                value= '',
                                on_change=lambda e: build_results(e.value))\
                                .props('autofocus clearable dense')
            self.search_box.on('keydown.enter', lambda e = self.search_box.value: build_results(e))
            #  TODO: Figure out how to make the input remember the last search
            
            loading = ui.spinner(size='md').classes('')
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
                    for item in results.json()['Results'][:10]  or []:  # iterate over the response data
                        with ui.row().on('click', lambda result_details= item: 
                                                    (self.item_selected(result_details['ID'])
                                                        )
                                        ).classes('items-center'):
                            ui.image(self.xiv.base_url + item['Icon']).classes('w-10')
                            ui.label(item['Name']) 
                
            self.search_box.bind_value(page,'last_search')
            search_results = ui.column()
            await build_results(self.search_box.value)
            loading.visible = False
            
    
    async def item_selected(self, item_id: int) -> None:
        
        ui.notify('Item Clicked: ' + str(item_id))
        layout.header.clear()
        layout.item_pane.clear()
        self.popup.close()
        
        with layout.header as container:
            loading = ui.spinner(size='md').classes('')
            item_json = await run.io_bound(self.xiv.get_item, item_id)
            loading.visible = False
   
            ui.image(self.xiv.base_url + item_json['Icon']).classes('w-10 min-w-[2.5rem]')
            ui.label(item_json['Name']).classes('text-h4')
            ui.label('iLvl: ' + str(item_json['LevelItem'])).classes('text-subtitle2')
                
        with layout.item_pane as container:
            container.classes('border-t-2')
            with ui.column():
                ui.html(item_json['Description']) if item_json['Description'] else None
                with ui.row():
                    ui.label('Craftable: Yes' if 'Recipes' in item_json else 'Craftable: No')
                    price = f'{str(item_json["PriceMid"])} gil' if 'GilShopItem' in item_json['GameContentLinks'] else 'No'
                    ui.label('Sold by Merchant: ' + price)
        
        with layout.search_history as container:
            ui.image(self.xiv.base_url + item_json['Icon']).classes('min-w-[3rem] min-h-[3rem]')\
                .on('click', lambda: self.item_selected(item_id)).move(target_index=0)
                #  TODO: Remove the item from the search history, since a new one will appear at the top
        
        self.populate_server_pane(item_id)
        
    def populate_server_pane(self, item_id):
        dc = "Elemental"
        with layout.server_pane as container:
            container.clear()
            
            world_prices = self.uc.market(item_id, dc)
            print(world_prices)
            jv.set_json(world_prices)
        
        
class JsonViewer:
    def __init__(self):
        with ui.right_drawer(fixed=False).style('background-color: #ebf1fa').props('bordered width=500 behavior=mobile') as right_drawer:
            self.jsonviewer = ui.json_editor(
                {'content': {'json': {}}}).classes('w-full')
        ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').classes('fixed top-2 right-[5rem]')

    def set_json(self, value):
        self.jsonviewer.properties["content"]["json"] = value
        self.jsonviewer.update()
        self.jsonviewer.run_editor_method(':expand', 'path => true')


jv = JsonViewer()
page = PageFunctionality('page')
layout = BasicContainers()


debug_ui = DebugUI(globalvar = vars(layout), 
                   pane_names = ['top_pane', 'bottom_pane', 'item_pane', 'server_pane', 'main_pane', 'sidebar'])

ui.run(show=False, port=8188, title='FFXIV Director',
       favicon='https://xivapi.com/favicon.ico')
