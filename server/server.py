import socket
import threading

HOST = "192.168.137.1"
PORT = 50000

def echo(conn):
    connections.append(conn)
    while data := conn.recv(1024):
        for c in connections:
            print('got', data)
            c.sendall(data)
    print("Connection lost to", conn.getpeername())
    connections.remove(conn)
    
def accept_connections(s):
    while True:
        conn, addr = s.accept()
        print("Connection accepted from", addr)
        t = threading.Thread(target = echo, args = (conn,))
        t.daemon = True
        t.start()

connections = []
s = socket.create_server((HOST, PORT))
s.listen()

t = threading.Thread(target=accept_connections, args = (s,))
t.daemon = True
t.start()

print('enter \'q\' to exit')
while True:
    cmd = input()
    if cmd == 'q':
        break
