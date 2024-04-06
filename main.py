import os
import json
import shutil
import requests

class VirtualFileSystem:
    def __init__(self, disk_path):
        self.disk_path = disk_path
        self.hostname = 'default_hostname'  # Set a default hostname value
        self.load_filesystem()
        self.current_user = 'root'
        self.current_directory = '/'
        self.users = {'root'}
        self.packages_directory = 'pkgs'
        self.system_directory = 'infosys'

    def load_filesystem(self):
        try:
            with open(self.disk_path, 'r') as file:
                data = json.load(file)
                self.root = data.get('root', {'/': {'root': {}}})
                self.hostname = data.get('hostname', 'default_hostname')
                self.users = set(data.get('users', ['root']))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            # If the file doesn't exist or is not in valid JSON format, create a new filesystem with default values
            self.root = {'/': {'root': {}}}
            self.hostname = 'default_hostname'
            self.users = {'root'}
            self.save_filesystem()

    def save_filesystem(self):
        with open(self.disk_path, 'w') as file:
            json.dump({'root': self.root, 'hostname': self.hostname, 'users': list(self.users)}, file)

    def mkdir(self, directory_path):
        path = self.resolve_path(directory_path)
        if path is not None:
            if self.check_permission(path):
                if path not in self.root:
                    self.root[path] = {self.current_user: {}}
                else:
                    print("Directory already exists.")
            else:
                print("Permission denied.")
        else:
            print("Invalid path.")
        # Обновляем каталоги в родительских каталогах
        parent_path = os.path.dirname(path)
        while parent_path not in ('', '/'):
            if parent_path not in self.root:
                self.root[parent_path] = {self.current_user: {}}
            elif self.current_user not in self.root[parent_path]:
                self.root[parent_path][self.current_user] = {}
            parent_path = os.path.dirname(parent_path)

    def cd(self, directory_path):
        path = self.resolve_path(directory_path)
        if path is not None:
            if path in self.root and isinstance(self.root[path], dict):
                self.current_directory = path
            else:
                print("Directory does not exist.")
        else:
            print("Invalid path.")

    def pwd(self):
        return self.current_directory

    def ls(self):
        current_dir = self.current_directory
        files = self.root.get(current_dir, {})
        print(list(files.keys()))

    def adduser(self, username):
        if self.current_user == 'root':
            if username not in self.users:
                self.users.add(username)
                print(f"User {username} added successfully.")
            else:
                print("User already exists.")
        else:
            print("Permission denied.")

    def change_hostname(self, new_hostname):
        self.hostname = new_hostname
        self.save_filesystem()

    def resolve_path(self, path):
        if path.startswith('/'):
            return path
        else:
            return os.path.join(self.current_directory, path)

    def check_permission(self, path):
        if self.current_user == 'root':
            return True
        elif self.current_user in self.root[path]:
            return True
        else:
            return False

    def help(self):
        print("Available commands:")
        print("mkdir <directory_path>: Create a new directory.")
        print("cd <directory_path>: Change directory.")
        print("ls: List directory contents.")
        print("pwd: Print working directory.")
        print("infoos: Display OS information.")
        print("adduser <username>: Add a new user.")
        print("host -e <new_hostname>: Change the hostname.")
        print("edit <filename>: Edit a file.")
        print("sudo <command>: Execute a command with superuser privileges.")
        print("su <username>: Switch user.")
        print("help: Display this help message.")
        print("clear: Clear the screen.")
        print("rm <file_path>: Remove a file or directory.")
        print("install_pkg <pkg_name>: Install a package.")
        print("remove_pkg <pkg_name>: Remove a package.")
        print("get <url> [filename]: Download a file from the internet.")
        print("cat <file_path>: Display the contents of a file.")

    def info_os(self):
        print("QwertyOS By AnmiTali taliildar Build 000012")
        print("license atos1.1")
        print("https://github.com/AnmiTali")
        print("Это не ОС это просто терминал, ядро или командная оболочка. Но скоро это будет операционой системой, эта оболочка не использует Linux это было написано с нуля.")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def rm(self, file_path):
        path = self.resolve_path(file_path)
        if path in self.root:
            del self.root[path]
            print(f"{file_path} removed successfully.")
        else:
            print("File or directory does not exist.")

    def install_packages(self):
        if not os.path.exists(self.packages_directory):
            os.makedirs(self.packages_directory)
            print("Created packages directory.")
        for root, dirs, files in os.walk(self.packages_directory):
            for file in files:
                pkg_name = os.path.basename(file)
                dest_path = os.path.join(self.current_directory, pkg_name)
                shutil.copy(os.path.join(root, file), dest_path)
                install_script_path = os.path.join(dest_path, 'install.py')
                if os.path.exists(install_script_path):
                    os.system(f'python {install_script_path}')
                print(f"{pkg_name} installed successfully.")

    def get(self, url, filename=None):
        response = requests.get(url)
        if response.status_code == 200:
            if filename is None:
                filename = os.path.basename(url)
            dest_path = os.path.join(self.current_directory, filename)
            with open(dest_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully: {filename}")
        else:
            print(f"Failed to download file from {url}")

    def cat(self, file_path):
        path = self.resolve_path(file_path)
        if os.path.exists(path) and os.path.isfile(path):
            with open(path, 'r') as file:
                print(file.read())
        else:
            print("File does not exist or is not a regular file.")

    def update_system_info(self):
        if not os.path.exists(self.system_directory):
            os.makedirs(self.system_directory)
        with open(os.path.join(self.system_directory, 'hostname'), 'w') as file:
            file.write(self.hostname)
        with open(os.path.join(self.system_directory, 'users'), 'w') as file:
            file.write('\n'.join(self.users))

class CommandProcessor:
    def __init__(self, disk_path):
        self.virtual_file_system = VirtualFileSystem(disk_path)

    def execute_command(self, command):
        command_parts = command.split()
        if command_parts[0] == 'mkdir':
            if len(command_parts) == 2:
                self.virtual_file_system.mkdir(command_parts[1])
            else:
                print("Usage: mkdir <directory_path>")
        elif command_parts[0] == 'cd':
            if len(command_parts) == 2:
                self.virtual_file_system.cd(command_parts[1])
            else:
                print("Usage: cd <directory_path>")
        elif command_parts[0] == 'ls':
            print(self.virtual_file_system.ls())
        elif command_parts[0] == 'pwd':
            print(self.virtual_file_system.pwd())
        elif command_parts[0] == 'adduser':
            if len(command_parts) == 2:
                self.virtual_file_system.adduser(command_parts[1])
            else:
                print("Usage: adduser <username>")
        elif command_parts[0] == 'host':
            if len(command_parts) == 3 and command_parts[1] == '-e':
                self.virtual_file_system.change_hostname(command_parts[2])
            else:
                print("Usage: host -e <new_hostname>")
        elif command_parts[0] == 'infoos':
            self.virtual_file_system.info_os()
        elif command_parts[0] == 'clear':
            self.virtual_file_system.clear_screen()
        elif command_parts[0] == 'rm':
            if len(command_parts) == 2:
                self.virtual_file_system.rm(command_parts[1])
            else:
                print("Usage: rm <file_path>")
        elif command_parts[0] == 'get':
            if len(command_parts) >= 2:
                url = command_parts[1]
                filename = command_parts[2] if len(command_parts) > 2 else None
                self.virtual_file_system.get(url, filename)
            else:
                print("Usage: get <url> [filename]")
        elif command_parts[0] == 'cat':
            if len(command_parts) == 2:
                self.virtual_file_system.cat(command_parts[1])
            else:
                print("Usage: cat <file_path>")
        elif command_parts[0] == 'install_pkg':
            if len(command_parts) == 2:
                self.virtual_file_system.install_pkg(command_parts[1])
            else:
                print("Usage: install_pkg <pkg_name>")
        elif command_parts[0] == 'remove_pkg':
            if len(command_parts) == 2:
                self.virtual_file_system.remove_pkg(command_parts[1])
            else:
                print("Usage: remove_pkg <pkg_name>")
        elif command_parts[0] == 'sudo':
            if len(command_parts) >= 2:
                self.virtual_file_system.sudo(' '.join(command_parts[1:]))
            else:
                print("Usage: sudo <command>")
        elif command_parts[0] == 'su':
            if len(command_parts) == 2:
                self.virtual_file_system.su(command_parts[1])
            else:
                print("Usage: su <username>")
        elif command_parts[0] == 'help':
            self.virtual_file_system.help()
        else:
            print("Command not found. Type 'help' for available commands.")

def main():
    disk_path = 'filesystem.json'
    command_processor = CommandProcessor(disk_path)
    while True:
        print(f"{command_processor.virtual_file_system.current_user}@{command_processor.virtual_file_system.hostname} {command_processor.virtual_file_system.current_directory} # ", end="")
        command = input()
        if command == 'exit':
            break
        command_processor.execute_command(command)

if __name__ == "__main__":
    main()
