#!/usr/bin/python3

import socket
import threading

# host = "145.24.222.172"
# port = 3306

host = "localhost"
port = 50000

class Robot:
    def __init__(self, conn, addr):
        self.name = conn.recv(1024).decode('utf-8')
        self.conn = conn
        
        print(f'{self.name} connected with address {addr}')
        connections.append(conn)
        runner = threading.Thread(target=self.run)
        runner.daemon = True
        runner.start()
    
    def run(self):
        try:
            while data := self.conn.recv(1024):
                for c in connections:
                    print(f'got {data} from {self.name}')
                    c.sendall(data)
        except:
            print(f'connection to {self.name} lost')
            connections.remove(self.conn)
    
def accept_connections(s):
    while True:
        conn, addr = s.accept()
        robot = Robot(conn, addr)

connections = []
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
