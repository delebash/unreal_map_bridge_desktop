# run.py
import webview
import waitress
from app import app
import pyautogui
import os
import signal
import argparse

parser = argparse.ArgumentParser("commandline_args")
parser.add_argument("--debug", help="Enables web browser debug tools defaults to false", dest='debug', type=bool,
                    default=False)
parser.add_argument("--host", help="Host string defaults to 127.0.0.1", dest='host', type=str, default='127.0.0.1')
parser.add_argument("--port", help="Port defaults to 5000", dest='port', type=int, default=5000)

args = parser.parse_args()

# debug = args.debug or False
# port = args.port or 5000
# host = args.host or '127.0.0.1'

width, height = pyautogui.size()
server = waitress.create_server(app, host=args.host, port=args.port)


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


window = webview.create_window('Unreal Map Bridge Desktop', url='http://localhost:5173/', height=height, width=width)
window.events.closed += on_closed
webview.start(func=custom_logic, args=window, debug=args.debug, private_mode=False)

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
