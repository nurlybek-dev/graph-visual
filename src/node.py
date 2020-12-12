import tkinter as tk
from string import ascii_uppercase
import math
from tkinter import font


LETTERS = ascii_uppercase.split()
CURRENT_INDEX = 0

def get_next_name():
    letters = list(ascii_uppercase)
    index = 0
    copy = 0
    while True:
        letter = letters[index] if copy < 1 else f'{letters[index]}{copy}'
        yield letter
        index += 1
        if index >= len(letters):
            index = 0
            copy += 1


name_generator = get_next_name()

def create_node(x, y, master):
    name = next(name_generator)
    node = Node(name, x, y, master)
    return {node.oval: node}


class Node(object):
    R = 20
    def __init__(self, name, x, y, master):
        self.x = x
        self.y = y
        self.name = name
        self.master = master
        self.canvas = master.canvas
        self.oval = self.canvas.create_oval(x-self.R, y-self.R, x+self.R, y+self.R, outline='black', fill='white', tag='node')
        self.label = self.canvas.create_text(x, y, text=self.name, justify=tk.CENTER, tag='label')
        self.result_label = None
        self.links = []

    def add_link(self, to):
        link = Link(self, to)
        self.links.append(link)

    def get_coords(self):
        return self.canvas.coords(self.oval)

    def get_center(self):
        coords = self.get_coords()
        x = (coords[0] + coords[2]) // 2
        y = (coords[1] + coords[3]) // 2
        return (x, y)

    def get_linked_nodes(self):
        return set(link.node_2 for link in self.links)

    def get_link_costs(self):
        return {link.node_2: link.distance for link in self.links}

    def find_lowest_distance_node(self, processed):
        lowest_distance = float('inf')
        lowest_distance_node = None

        for node, distance in self.get_link_distances().items():
            if distance < lowest_distance and node not in processed:
                lowest_distance = distance
                lowest_distance_node = node

        return lowest_distance_node

    def set_color(self, color):
        self.canvas.itemconfig(self.oval, fill=color)

    def set_result(self, distance):
        self.result_label = self.canvas.create_text(self.x, self.y + 10, text=str(distance), font='Arial 8 italic', justify=tk.CENTER, tag='result_label')

    def remove_result(self):
        if self.result_label:
            self.canvas.delete(self.result_label)
        self.result_label = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Node {self.name}>'


class Link(object):
    def __init__(self, node_1, node_2):
        self.node_1 = node_1
        self.node_2 = node_2
        self.distance = self.calculate_distance()
        self.lines = []
        self.create_line()
        self.create_distance_text()

    def calculate_distance(self):
        dx = self.node_1.get_center()[0] - self.node_2.get_center()[0]
        dy = self.node_1.get_center()[1] - self.node_2.get_center()[1]
        distance = int(math.sqrt(dx * dx + dy * dy))
        return distance

    def create_line(self):
        x, y = self.node_1.get_center()
        x1, y1 = self.node_2.get_center()
        line = self.node_1.canvas.create_line(x, y, x1, y1, tag='line')
        self.lines.append(line)
        
        self.create_line_head()

    def create_distance_text(self):
        x, y = self.node_1.get_center()
        x1, y1 = self.node_2.get_center()

        dx = x - x1
        dy = y - y1
        nx = dx / self.distance
        ny = dy / self.distance
        head_x = x - (Node.R * 2) * nx
        head_y = y - (Node.R * 2) * ny

        self.node_1.canvas.create_text(head_x, head_y, text=str(self.distance), justify=tk.CENTER, state=self.node_1.master.show_cost_state, tag='distance_tag')

    def create_line_head(self):
        x, y = self.node_1.get_center()
        x1, y1 = self.node_2.get_center()

        dx = x1 - x
        dy = y1 - y
        nx = dx / self.distance
        ny = dy / self.distance
        head_x = x1 - Node.R * nx
        head_y = y1 - Node.R * ny

        ax = (Node.R / 2) * (-ny - nx)
        ay = (Node.R / 2) * (nx - ny)

        line_head_1 = self.node_1.canvas.create_line(head_x + ax, head_y + ay, head_x, head_y, tag='line')
        line_head_2 = self.node_1.canvas.create_line(head_x, head_y, head_x - ay, head_y + ax, tag='line')

        self.lines.append(line_head_1)
        self.lines.append(line_head_2)
