from enum import Enum
import tkinter as tk
from PIL import Image, ImageTk

from .node import create_node, Node
from . import network


class Mode(Enum):
    NONE = 0
    ADD_NODE = 1
    ONE_WAY_LINK = 2
    TWO_WAY_LINK = 3
    DFS = 4
    BFS = 5
    DIJKSTRA = 6


class Menubar(tk.Menu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_menu = tk.Menu(self, tearoff=0)
        self.file_menu.add_command(label="Exit", command=self.on_exit)

        self.is_show_costs = tk.StringVar(value='normal')
        self.settings_menu = tk.Menu(self, tearoff=0)
        self.settings_menu.add_checkbutton(label='Show costs',
                                           onvalue='normal',
                                           offvalue='hidden',
                                           variable=self.is_show_costs,
                                           command=self.toggle_show_costs)

        self.add_cascade(label="File", menu=self.file_menu)
        self.add_cascade(label="Settings", menu=self.settings_menu)

    def on_exit(self):
        self.quit()

    def toggle_show_costs(self):
        self.master.on_toggle_show_costs(self.is_show_costs.get())


class Toolbar(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_node_button = ToggleImageButton(
            'OnAddNode', 'images/add_node.png', master=self)
        self.one_way_link_button = ToggleImageButton(
            'OnOneWayLink', 'images/add_link.png', master=self)
        self.two_way_link_button = ToggleImageButton(
            'OnTwoWayLink', 'images/add_link2.png', master=self)
        self.dfs = ToggleButton('OnDFS', 'DFS', master=self)
        self.bfs = ToggleButton('OnBFS', 'BFS', master=self)
        self.bfs = ToggleButton('OnDijkstra', 'Dijkstra', master=self)


class ToggleButton(tk.Button):
    def __init__(self, event_name, text, *args, **kwargs):
        self.event_name = event_name
        super().__init__(text=text, relief=tk.FLAT, command=self.click, *args, **kwargs)
        self.pack(side=tk.LEFT, padx=2, pady=2)
        self.is_active = False
        self.bind_all('<<OnUntoggleToolbar>>',
                      self.on_toolbar_button_clicked, True)

    def click(self):
        self.is_active = not self.is_active
        self.config(relief=tk.SUNKEN if self.is_active else tk.FLAT)
        self.event_generate(f'<<{self.event_name}>>')
        self.event_generate(f'<<OnUntoggleToolbar>>')

    def on_toolbar_button_clicked(self, event):
        if self != event.widget:
            self.is_active = False
            self.config(relief=tk.SUNKEN if self.is_active else tk.FLAT)


class ImageButton(tk.Button):
    def __init__(self, event_name, img_path, *args, **kwargs):
        self.event_name = event_name
        self.img = ImageTk.PhotoImage(Image.open(img_path))
        super().__init__(image=self.img, relief=tk.FLAT, command=self.click, *args, **kwargs)
        self.image = self.img
        self.pack(side=tk.LEFT, padx=2, pady=2)

    def click(self):
        self.event_generate(f'<<{self.event_name}>>')
        self.event_generate(f'<<OnUntoggleToolbar>>')


class ToggleImageButton(ImageButton):
    def __init__(self, event_name, img_path, *args, **kwargs):
        super().__init__(event_name, img_path, *args, **kwargs)
        self.is_active = False
        self.bind_all('<<OnUntoggleToolbar>>',
                      self.on_toolbar_button_clicked, True)

    def click(self):
        self.is_active = not self.is_active
        self.config(relief=tk.SUNKEN if self.is_active else tk.FLAT)
        super().click()

    def on_toolbar_button_clicked(self, event):
        if self != event.widget:
            self.is_active = False
            self.config(relief=tk.SUNKEN if self.is_active else tk.FLAT)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('800x600')
        self.title('Graph')

        self.menubar = Menubar(master=self)
        self.config(menu=self.menubar)

        self.toolbar = Toolbar(self, bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.canvas = tk.Canvas(self, bg='beige')
        self.canvas.pack(expand=1, fill=tk.BOTH)

        self.statusbar = tk.Label(
            self, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.bind('<<OnAddNode>>', self.on_add_node)
        self.bind('<<OnOneWayLink>>', self.on_one_way_link)
        self.bind('<<OnTwoWayLink>>', self.on_two_way_link)
        self.bind('<<OnDFS>>', self.on_dfs)
        self.bind('<<OnBFS>>', self.on_bfs)
        self.bind('<<OnDijkstra>>', self.on_dijkstra)
        self.bind('<<OnUntoggleToolbar>>', self.on_untoggle_toolbar)
        self.canvas.bind('<Button-1>', self.on_canvas_click)

        self.nodes = {}

        self.show_cost_state = 'normal'
        self.is_add_node = False
        self.mode = Mode.NONE

        self.first_node = None
        self.second_node = None
        self.link_mode = None

        self.toolbar_action = None

    def on_toggle_show_costs(self, state):
        self.show_cost_state = state
        self.canvas.itemconfig('distance_tag', state=state)

    def on_add_node(self, event):
        self.set_mode(Mode.ADD_NODE)

    def on_one_way_link(self, event):
        self.set_mode(Mode.ONE_WAY_LINK)

    def on_two_way_link(self, event):
        self.set_mode(Mode.TWO_WAY_LINK)

    def on_dfs(self, event):
        self.set_mode(Mode.DFS)

    def on_bfs(self, event):
        self.set_mode(Mode.BFS)

    def on_dijkstra(self, event):
        self.set_mode(Mode.DIJKSTRA)

    def on_untoggle_toolbar(self, event):
        self.reset()

    def set_mode(self, mode):
        if self.mode == mode:
            self.mode = Mode.NONE
        else:
            self.mode = mode

    def on_canvas_click(self, event):
        if self.mode == Mode.NONE:
            return

        if self.mode == Mode.ADD_NODE:
            self.add_node(event.x, event.y)
        else:
            self.on_node_click(event)

    def add_node(self, x, y):
        r = Node.R
        closest = self.canvas.find_overlapping(x + r, y + r, x - r, y - r)
        if len(closest) > 0:
            return

        node = create_node(x, y, self)
        self.nodes.update(node)

    def on_node_click(self, event):
        node_key = self.get_closest_node(event.x, event.y)
        if node_key is None:
            return
        node = self.nodes[node_key]

        if self.mode == Mode.ONE_WAY_LINK or self.mode == Mode.TWO_WAY_LINK:
            self.link(node)
        else:
            self.search(node)

    def link(self, node):
        if self.first_node == None:
            self.first_node = node
            self.first_node.set_color('pale green')
        elif self.first_node != node:
            self.second_node = node
            self.connect_nodes()

    def search(self, node):
        self.reset()
        if self.mode == Mode.DFS:
            self.dfs_search(node)
        elif self.mode == Mode.BFS:
            self.bfs_search(node)
        elif self.mode == Mode.DIJKSTRA:
            self.dijkstra_search(node)

    def dfs_search(self, node):
        visited = network.dfs(node)

        node.set_color('pale green')
        for n in visited:
            n.set_color('SkyBlue1')

        connected = ', '.join([str(node) for node in visited])
        status = f'{node} connected: with {connected}'
        self.statusbar.config(text=status)

    def bfs_search(self, node):
        visited = network.bfs(node)

        node.set_color('pale green')
        for n in visited:
            n.set_color('SkyBlue1')

        connected = ', '.join([str(node) for node in visited])
        status = f'{node} connected with: {connected}'
        self.statusbar.config(text=status)

    def dijkstra_search(self, node):
        costs, parents = network.dijkstra(node)
        node.set_color('pale green')
        for n, c in costs.items():
            n.set_color('SkyBlue1')
            n.set_result(c)

        connected = ', '.join(
            [f'{str(n)}: {str(c)}' for n, c in costs.items()])
        status = f'{node} connected with (node: cost): {connected}'
        self.statusbar.config(text=status)

    def get_closest_node(self, x, y):
        closest_nodes = self.canvas.find_overlapping(
            x + 0.1, y + 0.1, x - 0.1, y - 0.1)
        for node in closest_nodes:
            if 'node' in self.canvas.gettags(node):
                return node
        return None

    def connect_nodes(self):
        if self.mode == Mode.ONE_WAY_LINK:
            self.first_node.add_link(self.second_node)
        elif self.mode == Mode.TWO_WAY_LINK:
            self.first_node.add_link(self.second_node)
            self.second_node.add_link(self.first_node)

        self.canvas.update()
        self.canvas.tag_raise('node')
        self.canvas.tag_raise('label')

        self.reset()

    def reset(self):
        if self.first_node:
            self.first_node.set_color('white')
        if self.second_node:
            self.second_node.set_color('white')

        for node in self.nodes.values():
            node.set_color('white')
            node.remove_result()

        self.statusbar.config(text='')

        self.first_node = None
        self.second_node = None


if __name__ == '__main__':
    App().mainloop()
