import os

file_dir = os.path.dirname(os.path.abspath(__file__))

cmd = f"setx path {file_dir}"

if os.system(cmd) == 0:
    print("Added " + file_dir + " to path.")
