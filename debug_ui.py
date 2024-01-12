from nicegui import ui

class DebugUI:
    def __init__(self, globalvar, pane_names):
        self.pane_names = pane_names
        self.pane_classes = {name: f'bg-slate-{i*100}' for i, name in enumerate(self.pane_names, start=1)}
        self.debug = True
        self.globalvar = globalvar
        ui.button('', on_click=self.debug_toggle, icon='flip_to_front').classes('fixed top-2 right-4')
        self.debug_toggle()


    def debug_toggle(self):
        for pane, class_name in self.pane_classes.items():
            if self.debug:
                self.globalvar[pane].classes(class_name)
            else:
                self.globalvar[pane].classes(remove=class_name)
        ui.notify('Debug UI: Enabled' if self.debug else 'Debug UI: Disabled')
        self.debug = not self.debug




