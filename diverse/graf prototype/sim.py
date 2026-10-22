import pygame as pg
from graph import G, weighted_edge_list, adj_dict, nodes, node_pos
from math import pi
import json
from random import random
from time import time

from os import chdir
chdir("common/graf prototype")

from networkx.algorithms.approximation import traveling_salesman_problem, christofides

# pg setup
pg.init()
screen_mult = 1.75
screen_margin = 50
screen_margin_vector = pg.Vector2((screen_margin, screen_margin))

screen = pg.display.set_mode((330*screen_mult+2*screen_margin, 500*screen_mult+2*screen_margin))
clock = pg.time.Clock()
running = True

pg.font.init()

FONT = pg.font.Font("font.ttf", 18)

# graph visuals
edge_color = pg.color.Color(25, 50, 50)
edge_thickness = 6
node_size = 5
node_color = pg.color.Color(75, 125, 255)
background_color = pg.color.Color(200, 180, 145)

# special node colors
node_colors = {
    "START": pg.color.Color(50, 240, 50),
    "R1": pg.color.Color(240, 50, 50),
    "R2": pg.color.Color(240, 50, 50),
    "R3": pg.color.Color(240, 50, 50),
    "R4": pg.color.Color(240, 50, 50),
    "R5": pg.color.Color(240, 50, 50),
    "W1": pg.color.Color(240, 240, 240),
    "W2": pg.color.Color(240, 240, 240),
    "W3": pg.color.Color(240, 240, 240),
    "W4": pg.color.Color(240, 240, 240),
    "W5": pg.color.Color(240, 240, 240),
    "1": pg.color.Color(125, 25, 240),
    "2": pg.color.Color(125, 25, 240)
}

def xy_to_screen(v: pg.Vector2):
    v = v*100*screen_mult+screen_margin_vector
    return pg.Vector2((v.x, v.y*(-1)+screen.get_height())) + pg.Vector2(0, 80)

def draw_graph():
    for edge in weighted_edge_list:
        node1_pos = pg.Vector2(node_pos[edge[0]])
        node2_pos = pg.Vector2(node_pos[edge[1]])
        pg.draw.line(
            screen,
            edge_color, 
            xy_to_screen(node1_pos), 
            xy_to_screen(node2_pos), 
            edge_thickness
        )

def draw_nodes():
    for node in node_pos.keys():
        if node in node_colors.keys():
            col = node_colors[node]
        else:
            col = node_color

        pg.draw.circle(
            screen,
            col,
            xy_to_screen(pg.Vector2(node_pos[node])),
            node_size*screen_mult
        )


class Robot:
    def __init__(self, speed: float, rot_speed: float, path: list[str], color, text: str, finish_times: list):
        self.speed = speed
        self.rot_speed = rot_speed
        self. path = path

        self.color = color
        self.text = text

        self.path_index = 0
        self.current_node = path[0]
        self.target_node = path[1]
        self.pos = pg.Vector2(node_pos[self.current_node])

        self.direction = pg.Vector2.normalize(pg.Vector2(node_pos[self.target_node]) - pg.Vector2(node_pos[self.current_node]))

        self.finish_times = finish_times
        self.start_time = time()
        self.sb_added = False

    def move_towards(self, target_pos: tuple):
        target_direction = pg.Vector2.normalize(pg.Vector2(target_pos) - pg.Vector2(node_pos[self.current_node]))
        direction_diff = self.direction.angle_to(target_direction)

        cross = pg.Vector2.cross(self.direction, target_direction)

        if target_direction == self.direction:
            self.pos += self.direction*self.speed
        elif cross == 0:
            self.pos += self.direction*self.speed * -1

        if cross != 0:
            if abs(direction_diff) > self.rot_speed:
                self.direction = self.direction.rotate(self.rot_speed * cross/abs(cross))
            else:
                self.direction = target_direction

    def update(self):
        try:
            if self.path_index < len(self.path):
                if self.pos.distance_to(node_pos[self.target_node]) < self.speed:
                    self. pos = pg.Vector2(node_pos[self.target_node])
                    self.path_index += 1
                    self.current_node = self.path[self.path_index]
                    self.target_node = self.path[self.path_index+1]

                self.move_towards(node_pos[self.target_node])
        except:
            if not self.sb_added:
                self.finish_times.append(f"[{len(self.finish_times)+1}]: {self.text}: {round(time() - self.start_time , 2)}")
                self.sb_added = True

    def draw(self):
        pg.draw.polygon(screen, self.color, [
            xy_to_screen(self.pos + self.direction*0.2),
            xy_to_screen(self.pos + self.direction.rotate(90)*0.1),
            xy_to_screen(self.pos + self.direction.rotate(-90)*0.1),
        ],
        6
        )

        # draw text
        text_surface = FONT.render(self.text, True, self.color)
        screen.blit(text_surface, xy_to_screen(self.pos) + pg.Vector2(10, 10))


with open("optimal_paths_brute_force.json", "r", encoding="utf-8") as f:
    optimal_paths_brute_force = json.load(f)

with open("optimal_paths_dijkstra.json", "r", encoding="utf-8") as f:
    optimal_paths_dijkstra = json.load(f)

dijkstra_col1 = pg.color.Color(0, 255, 0)
dijkstra_col2 = pg.color.Color(0, 150, 100)

robot_speed = 0.05
robot_rot_speed = 7

finish_times = []

robots = [
    Robot(robot_speed, robot_rot_speed, optimal_paths_dijkstra["1"][1][1], dijkstra_col1.lerp(dijkstra_col2, 0), "n=1", finish_times),
    Robot(robot_speed, robot_rot_speed, optimal_paths_brute_force["best paths"][0], (255, 50, 50), "Bruteforce", finish_times),
    Robot(robot_speed, robot_rot_speed, optimal_paths_dijkstra["2"][1][1], dijkstra_col1.lerp(dijkstra_col2, 0.1), "n=2", finish_times),
    Robot(robot_speed, robot_rot_speed, optimal_paths_dijkstra["4"][1][1], dijkstra_col1.lerp(dijkstra_col2, 0.3), "n=4", finish_times),
    Robot(robot_speed, robot_rot_speed, optimal_paths_dijkstra["5"][1][1], dijkstra_col1.lerp(dijkstra_col2, 0.4), "n=5", finish_times),
    Robot(robot_speed, robot_rot_speed, optimal_paths_dijkstra["6"][1][1], dijkstra_col1.lerp(dijkstra_col2, 0.5), "n=6", finish_times),
    Robot(robot_speed, robot_rot_speed, optimal_paths_dijkstra["7"][1][1], dijkstra_col1.lerp(dijkstra_col2, 0.6), "n=7", finish_times),
    Robot(robot_speed, robot_rot_speed, optimal_paths_dijkstra["8"][1][1], dijkstra_col1.lerp(dijkstra_col2, 0.7), "n=8", finish_times),
    Robot(robot_speed, robot_rot_speed, optimal_paths_dijkstra["9"][1][1], dijkstra_col1.lerp(dijkstra_col2, 0.8), "n=9", finish_times),
    Robot(robot_speed, robot_rot_speed, optimal_paths_dijkstra["10"][1][1], dijkstra_col1.lerp(dijkstra_col2, 0.9), "n=10", finish_times),
    Robot(robot_speed, robot_rot_speed, optimal_paths_dijkstra["3"][1][1], (255, 135, 0), "n=3", finish_times)
]

def draw_scoreboard():
    sb_string = "Scoreboard:\n"
    for s in finish_times:
        sb_string += " " + s + "\n"
    sb_surface = FONT.render(sb_string, True, (30, 30, 250))
    screen.blit(sb_surface, (10, 10))

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill(background_color)

    draw_graph()
    draw_nodes()

    for robot in robots:
        robot.update()
        robot.draw()

    draw_scoreboard()

    pg.display.flip()

    clock.tick(60)

pg.quit()