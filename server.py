import socket
from select import select
from threading import Thread
import time
import json

class Server(Thread):
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", 48255))
        self.server.listen(5)

        self.users_list = []
        # IDE !!!

        Thread.__init__(self)

    def recv_timeout(self, socket, timeout=0.1):
        # http://www.binarytides.com/receive-full-data-with-the-recv-socket-function-in-python/
        # make socket non blocking
        socket.setblocking(0)

        # total data partwise in an array
        total_data=[];
        data='';

        # beginning time
        begin=time.time()
        while 1:
            # if you got some data, then break after timeout
            if total_data and time.time()-begin > timeout:
                break

            # if you got no data at all, wait a little longer, twice the timeout
            elif time.time()-begin > timeout*2:
                break

            # recv something
            try:
                data = socket.recv(8192)
                if data:
                    total_data.append(data)
                    # change the beginning time for measurement
                    begin=time.time()
                else:
                    # sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except:
                pass

        # join all parts to make final string
        return_data = list()
        for data in total_data:
            return_data.extend(data)
        return bytes(return_data)

    def send(self, socket, dictio):
        try:
            socket.send(json.dumps(dictio).encode("UTF-8"))
        except Exception as ex:
            print(ex)

    def run(self):
        new_users, wlist, xlist = select([self.server], [], [], 0.1)
        for new_user in new_users:
            client, client_info = self.server.accept()
            if client not in self.users_list:
                self.users_list.append(client)
            else:
                raise ValueError("Users already registered")

        new_messages, wlist, xlist = select(self.users_list, [], [], 0.1)
        for client in new_messages:
            try:
                data_json = json.loads(self.recv_timeout(client, 0.1).decode("UTF-8"))
            except Exception as ex:
                print(ex)

            print(data_json)
