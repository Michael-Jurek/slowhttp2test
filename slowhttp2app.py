

# HTTP/2 START CONNECTION FRAME
CONNECTION_PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
# 31-bit INTEGER indicating the number of octets the sender can transmit
# in current flow controll window
WINDOW_SIZE_INCREMENT = 2147483647

