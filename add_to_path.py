import os

file_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_dir)

print(os.system("path > path.txt"))
with open("path.txt") as f:
    paths = f.read().replace("PATH=", "").replace("\n", "").split(';')

if file_dir in paths:
    print(f"{file_dir} is already in PATH.")
else:
    cmd = f"setx path \"%path%;{file_dir}\""
    if os.system(cmd) == 0:
        print("Added " + file_dir + " to PATH.")
    else:
        print("Cannot add " + file_dir + " to PATH.")
