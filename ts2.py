import binascii
import socket
import sys
import argparse

dnsTable = {}

def construct_helper(i, j, res, inp):
    dname = inp[i:j]
    dlen = hex(len(dname))[2:]
    if len(dlen) == 1:
        res = res + "0" + dlen
    else:
        res = res + dlen
    res = res + binascii.hexlify(dname.encode()).decode()
    return res

def construct_udp_message(inp):
    res = ""
    i = 0
    j = inp.find(".")
    while j != -1:
        res = construct_helper(i, j, res, inp)
        i = j + 1
        j = inp.find(".", j+1)
    res = construct_helper(i, len(inp), res, inp) + "00 00 01 00 01"
    return "aa aa 01 00 00 01 00 00 00 00 00 00 " + res


def send_message(req):
    gsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serv_addr = ("1.1.1.1",53)
    try:
        gsock.sendto(binascii.unhexlify(req), serv_addr)
        data, _ = gsock.recvfrom(4096)
    finally:
        gsock.close()
    return binascii.hexlify(data).decode("utf-8")

def format_hex(hex):
    octets = [hex[i:i+2] for i in range(0, len(hex), 2)]
    pairs = [" ".join(octets[i:i+2]) for i in range(0, len(octets), 2)]
    return "\n".join(pairs)

def dns_lookup(data):
    message = construct_udp_message(data)
    message = message.replace(" ", "").replace("\n", "")
    answer = send_message(message)
    res = ""
    i = answer.find(message[24:])+len(message[24:])
    while i < len(answer):
        i = i + 4
        answerType = int(answer[i:i+4],16)
        i = i + 16
        rdLen = int(answer[i:i+4],16)
        i = i + 4
        if answerType != 1:
            if answerType == 6:
                res = res + data + " - Error:HOST NOT FOUND,"
            else:
                res = res + "other,"
        else:
            res = res + str(int(answer[i:i+2],16)) + "." + str(int(answer[i+2:i+4],16)) + "." + str(int(answer[i+4:i+6],16)) + "." + str(int(answer[i+6:i+8],16)) + ","
        i = i + (2*rdLen)
    dnsTable[data] = res[:len(res)-1]

def listen(portNo):   ##waiting for connection from client
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        host = socket.gethostname()
        print("The server host name is {}".format(host))
        s.bind(('', portNo))
        s.listen()
        conn, addr = s.accept()
        with conn:
            while True:
                data = conn.recv(1024).decode("utf-8")
                ##data is info sent by client
                if not data:
                    break
                data = data.lower()
                if data not in dnsTable:
                    dns_lookup(data)
                conn.sendall(dnsTable[data].encode('utf-8'))
        s.close()

if __name__ == '__main__':
    portNo = int(sys.argv[1])
    listen(portNo)