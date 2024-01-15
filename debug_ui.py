from nicegui import ui

class DebugUI:
    def __init__(self, container, panes: list, start=False):
        self.panes = panes
        self.debug = False
        if start:
            self.debug_toggle()
        with container:
            ui.button('', on_click=self.debug_toggle, icon='flip_to_front').props('round')
                

    def debug_toggle(self):
        self.debug = not self.debug
        ui.notify('Debug UI: Enabled' if self.debug else 'Debug UI: Disabled')
        for i, pane in enumerate(self.panes, start=1):
            if self.debug:
                pane.classes(f'bg-slate-{i*100}')
            else:
                pane.classes(remove=f'bg-slate-{i*100}')
        
class JsonViewer:
    def __init__(self, container):
        with ui.right_drawer(fixed=False).classes('text-xs').props('bordered behavior=mobile width=400') as right_drawer:
            self.jsonviewer = ui.json_editor(
                {'content': {'json': {}}}).classes('w-full')
        with container:
            ui.button(on_click=lambda: right_drawer.toggle(), icon='account_tree').props('round')

    def set_json(self, value):
        ui.notify('Updating JSON Viewer')
        self.jsonviewer.properties["content"]["json"] = value
        self.jsonviewer.update()
        self.jsonviewer.run_editor_method(':expand', 'path => true')

