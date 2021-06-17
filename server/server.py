#!/usr/bin/python3

import socket
import threading

# host = "145.24.222.172"
# port = 3306

host = "localhost"
port = 50000

class Robot:
    def __init__(self, conn, addr):
        incoming = conn.recv(1024).decode().split(' ', maxsplit=1)
        print('incoming', incoming)
        self.name = incoming[0]
        self.position = incoming[1]
        self.conn = conn
        
        print(f'{self.name} connected with address {addr} and is at {self.position}')
        robots.append(self)
        runner = threading.Thread(target=self.run)
        runner.daemon = True
        runner.start()
    
    def run(self):
        try:
            while data := self.conn.recv(1024):
                print(f'got {data} from {self.name}')
                for r in robots:
                    r.message(data)
        except:
            print(f'connection to {self.name} lost')
            robots.remove(self)
    
    def message(self, text):
        self.conn.sendall(text)
    
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
