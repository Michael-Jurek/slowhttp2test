from multiprocessing import Process

def info(title):
    

def f(name):
    print("hello", name)

if __name__ == '__main__':
    p = Process(target=f,args=('bob',))
    p.start()
    p.join()