#! /usr/bin/python

import threading

import time

import socket, sctp

import argparse

class Sender(threading.Thread):

    def __init__(self, sock, clients ):
        threading.Thread.__init__(self)
        self.sock = sock
        self.clients = clients
        print "OK"

    def run(self):
        counter = 1
        with open('sender.out', 'w') as out:
            out.write('Sender\n')
            out.flush()
            while True:
                out.write('clients')
                out.write(str(self.clients))
                out.write('\n')
                out.flush()
                for assocId, fromaddr in self.clients.items():
                    msg = "This is message #"+str(counter)+" for client "+str(assocId)
                    out.write('about to send\n')
                    out.flush()
                    self.sock.sctp_send(msg, to = fromaddr, stream = 3)
                    out.write(msg)
                    out.write('\n')
                    out.write('\n')
                    out.flush()
                time.sleep(0.5)
                counter += 1

class Server(object):

    def __init__(self):
        self.sock = sctp.sctpsocket_udp(socket.AF_INET)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.initparams.num_ostreams = 15
        self.sock.initparams.max_instreams = 20

        self.sock.events.clear()
        self.sock.events.data_io = True
        self.sock.events.association = True
        self.sock.events.shutdown = True

    def start(self, port):
        self.sock.bindx([("", port)])
        self.sock.listen(5)

        clients = {}

        sender = Sender(self.sock, clients)
        sender.setDaemon(True)
        sender.start()

        xxx = 2
        while xxx:
            xxx -= 1

            print 'waiting\n'
            fromaddr, flags, msgret, notif = self.sock.sctp_recv(3000)
            print 'done waiting\n'

            if flags & sctp.FLAG_NOTIFICATION:
                if notif.__class__ == sctp.assoc_change:
                    if notif.state == sctp.assoc_change.state_COMM_UP:
                        print('assoc change - comm up on assoc: ' + str(notif.assoc_id))
                        clients[notif.assoc_id] = fromaddr
                    elif notif.state == sctp.assoc_change.state_COMM_LOST:
                        print('assoc change - comm lost on assoc: ' + str(notif.assoc_id))
                        clients.pop(notif.assoc_id,None)
                elif notif.__class__ == sctp.shutdown_event:
                    print('shutdown on assoc: '+ str(notif.assoc_id))
                    clients.pop(notif.assoc_id,None)
            elif msgret == '':
                print('read EOF')
                continue
            time.sleep(5)

        self.sock.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Start a threaded SCTP server.')
    parser.add_argument('-port', dest='port', type=int, action='store', default=5005, help='the port the server listens to (default: 5005)')
    args = parser.parse_args()

    server = Server()
    server.start(args.port)
