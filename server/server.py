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
    return tuple(map(int, filter(str.isdigit, position)))

class Robot:
    def __init__(self, conn, addr):
        info = conn.recv(1024).decode().split(' ', maxsplit=1)

        self.name = info[0]
        self.position = position_from_string(info[1])
        self.conn = conn
        self.order = None
        self.target = None

        print(f'{self.name} connected with address {addr} and is at {self.position}')
    
    def give_order(self, order):
        self.order = order
        self.target = order[0]
    
def accept_connections(s):
    while True:
        conn, addr = s.accept()
        connection_requests.append((conn, addr))

def handle_input():
    print('enter \'q\' to exit')
    while True:
        cmd = input()
        if cmd == 'q':
            break
        elif cmd == 'add':
            orders.append(
                ((0, 0), (0, 3))
            )

def tick():
    if connection_requests:
        conn, addr = connection_requests.pop()
        robots.append(Robot(conn, addr))

    for robot in robots:
        if not orders:
            break

        order = orders.pop()
        robot.give_order(order)
        print(f'assigned {order} to {robot.name}')
    
    # first send all
    # then receive all
    try:
        for robot in robots:
            target = robot.target if robot.target != None else robot.position
            print(f'sending {target} to {robot.name}')
            robot.conn.sendall(position_to_string(target).encode())
            print(world.dijkstra(robot.position, robot.target))
        
        for robot in robots:
            print(f'waiting for response from {robot.name}')
            data = robot.conn.recv(1024)
            robot.position = position_from_string(data.decode())
            print(f'{robot.name} is at {robot.position}')

            if robot.position == robot.target:
                if robot.position == robot.order[0]:
                    # switch to destination
                    robot.target = robot.order[1]
                    print(f'{robot.name} got package at {robot.position}')
                else:
                    # done with order
                    robot.target = None
                    robot.order = None
                    print(f'{robot.name} delivered package at {robot.position}')

    except (ConnectionResetError, ConnectionAbortedError):
        print(f'connection to {robot.name} lost')
        robots.remove(robot)

def run():
    while True:
        tick()

orders = [
    ((1, 2), (3, 4)),
    ((4, 2), (1, 1)),
    ((3, 1), (0, 4)),
    ((4, 0), (0, 0))
]

world = dk.Map([
#     0    1    2    3    4    5   6    7    8    9   10
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
