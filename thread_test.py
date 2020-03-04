import threading
from datetime import datetime
import multiprocessing


def countdown():
    x = 1000000000
    while x>0:
        x-=1

def implementation1():
    thread1 = threading.Thread(target=countdown)
    thread2 = threading.Thread(target=countdown)
    thread3 = threading.Thread(target=countdown)
    thread1.start()
    thread2.start()
    thread3.start()
    thread1.join()
    thread2.join()
    thread3.join()

def implementation2():
    countdown()
    countdown()

def implementation3():
    process1 = multiprocessing.Process(target=countdown)
    process2 = multiprocessing.Process(target=countdown)
    process1.start()
    process2.start()
    process1.join()
    process2.join()

def main():
    now = datetime.now()
    implementation1()
    end = datetime.now()
    print("Multiprocess time: %s",str(end-now))

    now = datetime.now()
    implementation2()
    end = datetime.now()
    print("Simple process time: %s", str(end-now))
    
    now = datetime.now()
    implementation3()
    end = datetime.now()
    print("Multiprocessing time: %s", str(end-now))

if __name__ == '__main__':
    main()