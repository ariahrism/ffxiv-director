def display_graphs():
    #  https://github.com/zauberzeug/nicegui/discussions/2052
    #  https://github.com/railsjazz/peity_vanilla
    #  table.add_slot('body-cell-weight','<td :props="props"><span class="line">{{ props.value }}</span></td>')
    ui.run_javascript(
        'document.querySelectorAll(".line").forEach(e => peity(e, "line"))')

ui.button('access elements', on_click=display_graphs)

weights = '70, 75, 80, 73, 82'

with ui.card().tight():  # .classes('w-[150px] h-[50px]'):
    ui.html(
        """<span class="line" data-peity='{ "max": 100, "width": 150, "height": 50 }'>""" + weights + '</span>')
    
    
###############################################################################################

from nicegui import ui

ui.add_head_html(
    '<script src="https://cdn.jsdelivr.net/npm/peity-vanilla/dist/peity-vanilla.min.js"></script>')

columns = [
    {'name': 'name', 'label': 'Name', 'field': 'name', 'align': 'left'},
    {'name': 'age', 'label': 'Age', 'field': 'age'},
    {'name': 'weight', 'label': 'Weight', 'field': 'weight'}
]
rows = [
    {'name': 'Alice', 'age': 18, 'weight': '60, 65, 62, 63, 58'},
    {'name': 'Bob', 'age': 21, 'weight': '70, 75, 80, 73, 82'},
    {'name': 'Carol', 'age': 24, 'weight': '80, 85, 82, 83, 88'},
]
table = ui.table(columns=columns, rows=rows, row_key='name')



def display_graphs():
    #  https://github.com/railsjazz/peity_vanilla
    #  table.add_slot('body-cell-weight','<td :props="props"><span class="line">{{ props.value }}</span></td>')
    ui.run_javascript(
        'document.querySelectorAll(".line").forEach(e => peity(e, "line"))')


ui.button('access elements', on_click=display_graphs)

weights = '70, 75, 80, 73, 82'

with ui.card().tight():  # .classes('w-[150px] h-[50px]'):
    ui.html(
        """<span class="line" data-peity='{ "max": 100, "width": 150, "height": 50 }'>""" + weights + '</span>')


ui.run(show=False)
