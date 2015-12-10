#! /usr/bin/python


import threading

import time

import socket, sctp

import argparse

class Receiver(threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
        pass

    def notifHandler(self, notif, data, out):
        if notif.__class__ == sctp.assoc_change:
            if notif.state == sctp.assoc_change.state_COMM_UP:
                print('assoc change - comm up on assoc: ' + str(notif.assoc_id))
            elif notif.state == sctp.assoc_change.state_COMM_LOST:
                print('assoc change - comm lost on assoc: ' + str(notif.assoc_id))
        elif notif.__class__ == sctp.shutdown_event:
            print('shutdown on assoc: '+ str(notif.assoc_id))

    def msgHandler(self, msg, out):
        out.write('msg: ')
        out.write(msg)
        out.write('\n\n')
        out.flush()

    def run(self):
        with open('receiver.out', 'w') as out:
            out.write('Receiver\n')
            out.flush()
            data = ''
            while True:
                out.write('waiting\n')
                out.flush()
                fromaddr, flags, dataTmp, notif = self.sock.sctp_recv(3000)
                out.write('done waiting\n')
                out.flush()
                if flags & sctp.FLAG_NOTIFICATION:
                    self.notifHandler(notif, dataTmp, out)
                else:
                    data += dataTmp
                    if flags & sctp.FLAG_EOR:
                        self.msgHandler(data, out)
                        data = ''

class Client(object):

    def __init__(self):
        self.sock = sctp.sctpsocket_udp(socket.AF_INET)

        self.sock.initparams.num_ostreams = 15
        self.sock.initparams.max_instreams = 20

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self, ip, port):
        server_tupel = ('127.0.0.1', 5005)

        self.sock.connect_ex(server_tupel)

        receiver = Receiver(self.sock)
        receiver.setDaemon(True)
        receiver.start()

        while True:
            print "stuff\n"
            time.sleep(2)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Start a threaded SCTP server.')
    parser.add_argument('-ip', dest='ip', type=str, action='store', default='127.0.0.1', help='the ip address the client connects to (default: \'127.0.0.1\')')
    parser.add_argument('-port', dest='port', type=int, action='store', default=5005, help='the port the client connects to (default: 5005)')
    args = parser.parse_args()

    client = Client()
    client.start(args.ip, args.port)
