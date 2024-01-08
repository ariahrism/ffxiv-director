from nicegui import run, ui
from xivapi_connection import XIVAPIConnection
import requests


class JsonViewer:
    def __init__(self):
        self.jsonviewer = ui.json_editor(
            {'content': {'json': {}}}).classes('w-[600px]')

    def set_json(self, value):
        self.jsonviewer.properties["content"]["json"] = value
        self.jsonviewer.update()
        self.jsonviewer.run_editor_method(':expand', 'path => true')


xiv = XIVAPIConnection()


async def populate_search(input_value):
    search_table.visible = False
    search_loading.visible = True
    call = await run.io_bound(xiv.search_for_item, input_value)
    jv.set_json(call)
    results = call['Results']
    search_table.rows.clear()
    search_loading.visible = False
    recipes_row.clear()
    for result in results:
        search_table.add_rows({
            'id': result['ID'],
            'icon': xiv.base_url + result['Icon'],
            'name': result['Name'],
            'url': xiv.base_url + result['Url'],
            'urltype': result['UrlType']
        })
    search_table.visible = True


async def show_recipe_details(item_id, container):
    """
    Shows the details of an items recipes in cards
    :param item_id:
    :return:
    """
    search_table.visible = False
    ui.notify('Item Clicked: ' + str(item_id))
    item_json = xiv.get_item(item_id)
    container.clear()
    with container:
        for recipe_id in item_json['Recipes']:
            card = ui.card()
            card.visible = False
            loading = ui.spinner('facebook', size='xl').classes('ml-14')
            recipe_json = await run.io_bound(xiv.get_recipe, recipe_id['ID'])
            with card.on('click', lambda e, t=recipe_json: (ui.notify('Recipe Clicked:' + str(t['ID'])), jv.set_json(t))).classes('w-[175px]'):
                with ui.row().classes('w-full'):
                    with ui.column():
                        ui.label(recipe_json['ClassJob']['NameEnglish'])
                        ui.label(
                            'Level: ' + str(recipe_json['RecipeLevelTable']['ClassJobLevel']))
                    ui.space()
                    with ui.column():
                        ui.image(
                            xiv.base_url + recipe_json['ClassJob']['Icon']).classes('w-[30px] h-[30px]')
                ui.separator()
                for i in range(10):
                    ingredient_amount = 'AmountIngredient' + str(i)
                    ingredient_details = 'ItemIngredient' + str(i)
                    if recipe_json.get(ingredient_details) is not None:
                        with ui.row().classes('w-full items-center'):
                            ui.image(
                                xiv.base_url + recipe_json[ingredient_details]['Icon']).classes('w-[30px] h-[30px]')
                            ui.label(str(
                                recipe_json[ingredient_amount])+'x ' + recipe_json[ingredient_details]['Name'])
            loading.visible = False
            card.visible = True
    jv.set_json(item_json)


async def show_something(seconds):
    for second in seconds:
        URL = 'https://httpbin.org/delay/'+str(second)
        response = await run.io_bound(requests.get, URL, timeout=5)
        ui.label(f'{second}: Downloaded {len(response.content)} bytes')

search_columns = [
    {'name': 'icon', 'label': 'Icon', 'field': 'icon'},
    {'name': 'name', 'label': 'Name', 'field': 'name'},
    {'name': 'urltype', 'label': 'Type', 'field': 'urltype'}
]
with ui.row().classes('w-full h-full'):
    with ui.column().classes('h-full'):
        with ui.row().classes('h-10'):
            input_box = ui.input('Search for an item', value='Iron Ingot',
                                 placeholder='Search for an item').props('autofocus clearable dense')
            # with input_box:
            ui.button('', on_click=lambda: populate_search(
                input_box.value), icon='search')

        with ui.row():
            with ui.row():
                search_loading = ui.spinner(size='xl').classes('m-14')
                search_loading.visible = False
                search_table = ui.table(columns=search_columns,
                                        rows=[], row_key='id')
                search_table.visible = False
                search_table.add_slot('body-cell-icon', '''
                    <q-td :props="props">
                        <q-img
                        :src="props.value"
                        spinner-color="black"
                        style="height: 40px; width: 40px"
                        />
                    </q-td>
                ''')

                selection = 0
                recipes_row = ui.row().classes('w-full h-40 items-center')
                search_table.on('rowClick',
                                lambda e: (
                                    # e.args[0] has NiceGUI metadata, e.args[1] has the row data
                                    # this function cannot take any other arguments or it will crash
                                    show_recipe_details(
                                        e.args[1]['id'], container=recipes_row)
                                )
                                )
    ui.space()

    with ui.card():
        jv = JsonViewer()
ui.run(show=False)
