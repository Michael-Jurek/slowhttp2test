import multiprocessing
from datetime import datetime

from hyper import HTTP20Connection
import requests

import slowhttp2app
from csv_handler import CSVHandler
from math import trunc

class WebServerStatus():
    def __init__(self, address, port):
        self.address = address
        self.port = port

    def check_h11server(self):
        r = requests.head("http://"+str(self.address)+":"+str(self.port))
        return r.status_code == 200

    def check_h2server(self):
        conn = HTTP20Connection(self.address, port=self.port)
        conn.request("GET", "/")
        resp = conn.get_response()
        return resp.status == 200


class Timer():
    def __init__(self, method, time_step):
        timer = multiprocessing.Process(target=method)
        timer.start()
        timer.join()
        self.time_step = time_step
        self.start = datetime.now()

    def stop(self):
        while True:
            end = datetime.now() - self.start
            seconds = end.seconds
            microsec = end.microseconds
            if((seconds + microsec / 100000) % self.time_step == 0):
                return datetime.now() - self.start

def main():

    try:
        # CASOVANI CASOVY KROK 0.1 s
        status = WebServerStatus("10.0.0.2","80")
        timer = Timer(status.check_h11server, 0.1)
        print(timer.stop())
        timer = Timer(status.check_h2server, 0.1)
        print(timer.stop())
    except KeyboardInterrupt:
        exit
        

if __name__ == '__main__':
    main()