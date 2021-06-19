#!/usr/bin/python3

import socket
import threading

# host = "145.24.222.172"
# port = 3306

host = "localhost"
port = 50000

def position_to_string(position):
    return '[' + str(position[0]) + ', ' + str(position[1]) + ']'

def position_from_string(position):
    position = ''.join([c for c in position if c.isdigit() or c == ' '])
    return position.split(' ', maxsplit=1)

class Robot:
    def __init__(self, conn, addr):
        info = conn.recv(1024).decode().split(' ', maxsplit=1)
        self.name = info[0]
        self.position = position_from_string(info[1])
        self.conn = conn
        
        print(f'{self.name} connected with address {addr} and is at {self.position}')

        robots.append(self)

        runner = threading.Thread(target=self.run)
        runner.daemon = True
        runner.start()
    
    def run(self):
        try:
            while data := self.conn.recv(1024):
                self.position = position_from_string(data.decode())
                print(f'{self.name} is at {self.position}')
        except (ConnectionResetError, ConnectionAbortedError):
            print(f'connection to {self.name} lost')
            robots.remove(self)
    
def accept_connections(s):
    while True:
        conn, addr = s.accept()
        robot = Robot(conn, addr)

robots = []
s = socket.create_server((host, port))
s.listen()

t = threading.Thread(target=accept_connections, args = (s,))
t.daemon = True
t.start()

print('enter \'q\' to exit')
while True:
    cmd = input()
    if cmd == 'q':
        break
