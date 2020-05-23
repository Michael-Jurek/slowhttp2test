import sys
import logging
import argparse
import textwrap
import urllib3
import time
import requests
import threading
import csv
from hyper import HTTP20Connection
from hyper.http20.exceptions import ConnectionError

# Parse input args
PARSER = argparse.ArgumentParser(description=textwrap.dedent('''\
                                SlowHTTP/2 Test Attack
                                
                                author: Michael Jurek
                                        xjurek03@stud.feec.vutbr.cz

                                run info:
                                1) Ensure to have created and activated virtual environment
                                   (e.g. python3 -m venv venv, source venv/bin/activate)
                                2) Ensure to have installed necessary packages
                                   (pip install -r requirements.txt)
                                3) Run attack: python3 %(prog)s ....'''),
                                formatter_class=argparse.RawTextHelpFormatter)
PARSER.add_argument("target", metavar="HOST",
                    type=str, help="IP address of a victim")
PARSER.add_argument("type", metavar="ATTACK", 
                    choices=['read', 'post', 'preface', 'headers', 'settings'],
                    type=str, help=textwrap.dedent('''\
                    Type of Slow DoS Attack
                    read      -- SLOW READ ATTACK
                    post      -- SLOW POST ATTACK
                    preface   -- SLOW PREFACE ATTACK
                    headers   -- SLOW HEADERS ATTACK
                    settings  -- SLOW SETTINGS ATTACK'''))

PARSER.add_argument("-p", "--port", metavar="port", type=int, default=80,
                    help="port of web application (80 default)")
PARSER.add_argument("-o", "--out", metavar="file",
                    type=str, default="output", help="name of output .csv and .html files")
PARSER.add_argument("-c", "--connection", metavar="connections", type=int, default=10,
                    help="number of parallel connections to webserver (10 default)")
PARSER.add_argument("-v", "--verbal", action="store_true", help="verbal output of attack - logged steps")
args = PARSER.parse_args()

# Logger setup
LOGGER = logging.Logger(name="slowhttp2test")
handler = logging.StreamHandler(sys.stdout)
if (args.verbal):
    handler.setLevel(logging.INFO)
else:
    handler.setLevel(logging.ERROR)
LOGGER.addHandler(handler)


class WebServerStatus():
    """Checks for web server availability"""
    def __init__(self, address, port):
        self.address = address
        self.port = port
    
    def check_server(self):
        http = urllib3.PoolManager()
        try:
            r = http.request("GET", "http://"+str(self.address)+":"+str(self.port), timeout=0.1)
            return r.status == 200
        except urllib3.exceptions.HTTPError as error:
            return False
        
    def check_serverh1(self):
        r = requests.head("http://"+str(self.address)+":"+str(self.port), timeout=0.1)
        return r.status_code == 200
    
    def check_serverh2(self):
        try:
            conn = HTTP20Connection(self.address, port=self.port)
            conn.request("GET","/")
            resp = conn.get_response()
            return resp.status == 200
        except ConnectionError as error:
            return False


class CSVHandler():
    """Handles I/O to database (.csv) file"""
    def __init__(self, mode="w", data=None):
        self.file = str(args.out+".csv")
        if mode in ["r", "w"]:
            self.mode = mode
        else:
            raise(Exception("Inavlid mode for csv operation"))
        self.data = data
        self._lock = threading.Lock()

    def write(self, data):
        with open(self.file, mode="w") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(data)
    
    def locked_write(self, data):
        num = data[0]
        LOGGER.info("Thread %s: starting update", num)
        LOGGER.info("Thread %s: about to lock", num)
        with self._lock():
            LOGGER.info("Thread %s: has lock", num)
            with open(self.file, mode="a") as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(data)
            LOGGER.info("Thread %s: releasing lock", num)
        LOGGER.info("Thread %s: finishing writing to database", num)


class Timer():
    """Creates time steps for launching an attack"""
    def __init__(self, time_step):
        self.time_step = time_step
        self.start = time.time()
    
    def step(self):
        while True:
            step = time.time() - self.start()
            if(step % self.time_step == 0):
                return step