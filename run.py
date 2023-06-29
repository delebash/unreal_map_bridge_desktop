# run.py
from waitress import serve
from app import app  # Import your app
# import easygui
# import os, sys

port = 5000
host = '127.0.0.1'
# Run from the same directory as this script
# this_files_dir = os.path.dirname(os.path.abspath(__file__))
# os.chdir(this_files_dir)

serve(app, host=host, port=port)


# def exit_program():
#     print("Exiting the program...")
#     sys.exit(0)
#
#
# msg = "Server Running..."
# title = "Unreal Map Bridge Server"
# choices = ["Quit"]
# reply = easygui.buttonbox(msg, title, choices=choices)
# if reply == "Quit":
#     exit_program()
# elif reply == "Stop Server":
#     os.startfile("C:\\Users\\lespo\\AppData\\Local\\slack\\slack.exe")
# else:
#     print("Done")
