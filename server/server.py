#!/usr/bin/python3

import socket
import threading
import dijkstra as dk
import random

# host = "145.24.222.172"
# port = 3306

host = "localhost"
port = 50000

def position_to_string(position):
    return str(position)

def position_from_string(position):
    filtered = ''.join([c for c in position if c.isdigit() or c == ' '])
    split = filtered.split(' ')
    nums = tuple(map(int, split))
    return nums

class Robot:
    def __init__(self, conn, addr):
        info = conn.recv(1024).decode().split(' ', maxsplit=1)

        self.name = info[0]
        self.position = position_from_string(info[1])
        self.conn = conn
        self.order = None
        self.target = self.position
        self.next_step = None

        print(f'{self.name} connected with address {addr} and is at {self.position}')
    
    def give_order(self, order):
        self.order = order
        self.target = order[0]
    
    def next_position(self):
        if self.order == None:
            print(f'{self.name} has no order and will move randomly')
            return self.random_step()
        
        try:
            path = world.dijkstra(self.position, self.target)
            print(f'{self.name} path: {path}')
        except dk.NoPathError as e:
            print(e.message)
            print(f'falling back on current position')
            return self.position

        if not path: # happens when the position == the target
            return self.position
        else:
            return path[0]
    
    def random_step(self):
        while True:
            possibilities = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            step = possibilities[random.randint(0, len(possibilities) - 1)]
            position = (self.position[0] + step[0], self.position[1] + step[1])
            if (
                not (world.at(position).is_obstacle or world.at(position).is_temporary_obstacle)
                and world.in_bounds(position)
            ):
                return position


def accept_connections(s):
    while True:
        conn, addr = s.accept()
        connection_requests.append((conn, addr))

def handle_input():
    global paused

    print('enter \'quit\' or \'q\' to exit')
    print('enter \'pause\' or \'p\' to pause')
    print('enter \'\orders\' or \'o\' to view all unhandled orders')
    print('enter \'add [x0] [y0] [x1] [y1]\' to add an order')

    while True:
        line = input().split(' ')
        cmd, args = line[0], line[1:]
        if cmd == 'quit' or cmd == 'q':
            break
        elif cmd == 'add':
            if len(args) != 4:
                print('usage: add [x0] [y0] [x1] [y1]')
            else:
                try:
                    x0, y0, x1, y1 = int(args[0]), int(args[1]), int(args[2]), int(args[3])
                    order = ((x0, y0), (x1, y1))
                    orders.append(order)
                    print(f'added order {order}')
                except ValueError:
                    print('error: could not convert input to position')
        elif cmd == 'pause' or cmd == 'p':
            paused = not paused
            print(f'paused: {paused}')
        elif cmd == 'orders' or cmd == 'o':
            print(orders)
        else:
            print('unknown command')

def tick():
    if connection_requests:
        conn, addr = connection_requests.pop()
        robots.append(Robot(conn, addr))

    for robot in robots:
        if not orders:
            break

        if robot.order == None:
            order = orders.pop()
            robot.give_order(order)
            print(f'assigned {order} to {robot.name}')
    
    # first send all
    # then receive all
    try:
        for robot in robots:
            next_step = robot.next_position()
            print(f'sending {next_step} to {robot.name} (and reserving spot)')
            robot.conn.sendall(position_to_string(next_step).encode())
            world.set_temporary_obstacle(next_step)
        
        for robot in robots:
            print(f'waiting for response from {robot.name}')
            data = robot.conn.recv(1024)
            robot.position = position_from_string(data.decode())
            print(f'{robot.name} is at {robot.position}')

            if robot.position == robot.target and robot.order != None:
                if robot.position == robot.order[0]:
                    # switch to destination
                    robot.target = robot.order[1]
                    print(f'{robot.name} got package at {robot.position}')
                else:
                    # done with order
                    robot.order = None
                    print(f'{robot.name} delivered package at {robot.position}')

    except (ConnectionResetError, ConnectionAbortedError):
        print(f'connection to {robot.name} lost')
        robots.remove(robot)
    
    world.clear_temporary_obstacles()
    if robots:
        print('')

def run():
    while True:
        if not paused:
            tick()

orders = [
    ((6, 3), (7, 3)),
    ((2, 3), (1, 3)),
    ((0, 0), (1, 1))
]

world = dk.Map([
#     0    1    2    3    4    5    6    7    8    9   10
    ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], # 0
    ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], # 1
    ['.', '.', 'O', 'O', 'O', 'O', 'O', 'O', 'O', '.', '.'], # 2
    ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], # 3
    ['.', '.', 'O', 'O', 'O', 'O', 'O', 'O', 'O', '.', '.'], # 4
    ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], # 5
    ['.', '.', 'O', '.', 'O', '.', 'O', '.', 'O', '.', '.'], # 6
    ['.', '.', 'O', '.', 'O', '.', 'O', '.', 'O', '.', '.'], # 7
    ['.', '.', 'O', '.', 'O', '.', 'O', '.', 'O', '.', '.'], # 8
    ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], # 9
    ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], # 10
  
    
])

paused = False
connection_requests = []
robots = []
s = socket.create_server((host, port))
s.listen()

accepter = threading.Thread(target=accept_connections, args=(s,))
accepter.daemon = True
accepter.start()

runner = threading.Thread(target=run)
runner.daemon = True
runner.start()

handle_input()
