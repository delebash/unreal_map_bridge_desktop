# run.py
import webview
import waitress
from app import app
import pyautogui
import os
import sys
import signal

debug = False
port = 5000
host = '127.0.0.1'
args = sys.argv
if len(args) > 1:
    if args[1] == '--debug':
        debug = True

width, height = pyautogui.size()
server = waitress.create_server(app, host=host, port=port)


def on_closed():
    print('Unreal Map Bridge is closing')
    shutdown_server()


def shutdown_server():
    print('Stop')
    pid = os.getpid()  # Get process ID of the current Python script
    os.kill(pid, signal.SIGINT)


def custom_logic(window):
    print('Start')
    server.run()


window = webview.create_window('Unreal Map Bridge', url='https://map.justgeektechs.com', height=height, width=width)
window.events.closed += on_closed
webview.start(func=custom_logic, args=window, debug=debug, private_mode=False)

# @route('/stop')
# def handle_stop_request():
#     # Handle "stop server" request from client: start a new thread to stop the server
#     Thread(target=shutdown_server).start()
#     return ''

# def callback(result):
#     print(result)


# def on_shown():
#     print(window)


# def close_dev_window():
# result = window.evaluate_js(
#     r"""
#     // Return user agent
#     'User agent:\n' + browser;
#     """
# )
#
# print(result)
