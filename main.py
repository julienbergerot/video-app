from src.controler import *

if __name__ == '__main__':
    # init the controler
    c = Controler(Model(),MyView())
    # start the app
    c.start()