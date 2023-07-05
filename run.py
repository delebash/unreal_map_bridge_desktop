# run.py

import webview
import waitress
from app import app
import pyautogui
import os, time, signal

port = 5000
host = '127.0.0.1'

width, height = pyautogui.size()
server = waitress.create_server(app, host=host, port=port)


def on_closed():
    shutdown_server()
    print('Unreal Map Bridge is closing')


# @route('/stop')
# def handle_stop_request():
#     # Handle "stop server" request from client: start a new thread to stop the server
#     Thread(target=shutdown_server).start()
#     return ''


def shutdown_server():
    # time.sleep(2)
    pid = os.getpid()  # Get process ID of the current Python script
    os.kill(pid, signal.SIGINT)
    # Kill the current script process with SIGINT, which does same as "Ctrl-C"


def custom_logic(window):
    print('Start')
    server.run()


window = webview.create_window('Unreal Map Bridge', url='https://map.justgeektechs.com', height=height, width=width)
window.events.closed += on_closed
webview.start(custom_logic, window)
