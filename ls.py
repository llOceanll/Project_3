import socket
import sys
import argparse

def listen(portNo):   ##waiting for connection from client
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        host = socket.gethostname()
        print("The server host name is {}".format(host))
        s.bind(('', portNo))
        s.listen()
        conn, addr = s.accept()
        with conn:
            try:
                ts1_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ts2_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print("[LS]: TS sockets created")
            except socket.error as err:
                print('Socket open error: {} \n'.format(err))
                exit()
            
            ts1_addr = (sys.argv[2], int(sys.argv[3]))
            ts2_addr = (sys.argv[4], int(sys.argv[5]))
            ts1_sock.settimeout(5.0)
            ts2_sock.settimeout(5.0)
            ts1_sock.connect(ts1_addr)
            ts2_sock.connect(ts2_addr)

            while True:
                data = conn.recv(1024).decode("utf-8")
                ##data is info sent by client
                if not data:
                    break
                data = data.lower()
                if hash(data)%2 == 0:
                    try:
                        ts1_sock.sendall(data.encode('utf-8'))
                        answer = ts1_sock.recv(1024)
                        answer = answer.decode('utf-8')
                        conn.sendall(answer.encode('utf-8'))
                    except socket.timeout:
                        try:
                            ts2_sock.sendall(data.encode('utf-8'))
                            answer = ts2_sock.recv(1024)
                            answer = answer.decode('utf-8')
                            conn.sendall(answer.encode('utf-8'))
                        except socket.timeout:
                            answer = data + " - Error:HOST NOT FOUND"
                            conn.sendall(answer.encode('utf-8'))
                else:
                    try:
                        ts2_sock.sendall(data.encode('utf-8'))
                        answer = ts2_sock.recv(1024)
                        answer = answer.decode('utf-8')
                        conn.sendall(answer.encode('utf-8'))
                    except socket.timeout:
                        try:
                            ts1_sock.sendall(data.encode('utf-8'))
                            answer = ts1_sock.recv(1024)
                            answer = answer.decode('utf-8')
                            conn.sendall(answer.encode('utf-8'))
                        except socket.timeout:
                            answer = data + " - Error:HOST NOT FOUND"
                            conn.sendall(answer.encode('utf-8'))
            ts1_sock.close()
            ts2_sock.close()
        s.close()

if __name__ == '__main__':
    portNo = int(sys.argv[1])
    listen(portNo)