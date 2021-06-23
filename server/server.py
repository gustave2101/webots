#!/usr/bin/python3

import socket
import threading
import dijkstra as dk

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
        self.target = None
        self.next_step = None

        print(f'{self.name} connected with address {addr} and is at {self.position}')
    
    def give_order(self, order):
        self.order = order
        self.target = order[0]
    
    def next_position(self):
        path = world.dijkstra(self.position, self.target)
        print(f'{self.name} path: {path}')

        if not path: # happens when the position == the target
            return self.position
        else:
            return path[0]


def accept_connections(s):
    while True:
        conn, addr = s.accept()
        connection_requests.append((conn, addr))

def handle_input():
    global paused

    print('enter \'q\' to exit')
    while True:
        cmd = input()
        if cmd == 'q':
            break
        elif cmd == 'add':
            orders.append(
                ((1, 2), (7, 7))
            )
        elif cmd == 'p':
            paused = not paused
            print(f'paused: {paused}')

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
            print(f'sending {next_step} to {robot.name}')
            robot.conn.sendall(position_to_string(next_step).encode())
        
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

def run():
    while True:
        if not paused:
            tick()

orders = [
    ((9, 8), (10, 6)),
    ((9, 2), (2, 5)),
    ((6, 3), (1, 8)),
    ((8, 0), (5, 3))
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
