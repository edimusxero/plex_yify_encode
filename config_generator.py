#!/usr/bin/python3
'''Generate config file'''

import os
import sys
import json
from pathlib import Path


class ConfigJSON:
    '''Group of all functions that create and modify Config.json .'''

    def __init__(self):
        '''Initialize main dir path used in several methods.'''
        self.dir = os.path.dirname(os.path.abspath(__file__))

    def change(self):
        '''Allows user to select an attribute in cofig.json and change it.'''

        while True:
            print("1. Change MYSQL Server")
            print("2. Change Server Port")
            print("3. Change Database")
            print("4. Change User Name")
            print("5. Change Password")
            print("6. Show Current Config")
            print("7. Quit\n")

            option = input(" >>  ")
            print()

            if not option or option == "7":
                print("Done...\n")
                sys.exit()

            elif option == "1":
                self.option_create("server")

            elif option == "2":
                self.option_create("port")

            elif option == "3":
                self.option_create("data_base")

            elif option == "4":
                self.option_create("user_name")

            elif option == "5":
                self.option_create("password")

            elif option == "6":
                self.view_config()

            else:
                print("Input not valid. \n")


    def option_create(self, name):
        '''Create option to be displayed when change is triggered.'''

        config_path = os.path.join(self.dir, "config.json")

        value = getattr(self, name)()

        with open(config_path) as config:
            data = json.load(config)
            data[name] = value

        with open(config_path, "w") as config:
            json.dump(data, config)

        print("\nDone\n")


    def config_create(self):
        '''Creates config.json.'''
        config_path = os.path.join(self.dir, "config.json")
        server = self.server()
        print()
        port = self.port()
        print()
        user_name = self.user_name()
        print()
        password = self.password()
        print()
        data_base = self.data_base()
        print()

        data = {
            "server": str(server),
            "port": str(port),
            "user_name": str(user_name),
            "password": str(password),
            "data_base": str(data_base)
        }

        with open(config_path, "w") as config:
            json.dump(data, config)
        print("\nDone.\n")


    @staticmethod
    def server():
        '''Set MYSQL Server'''
        print("Enter the MYSQL Server Address\n")
        while True:
            server = input(" >>  ")
            if server:
                print(f"MYSQL Server Address: {server}")
                return server.strip()


    @staticmethod
    def port():
        '''Set MYSQL Port'''
        print("Enter the MYSQL Port: \n")
        while True:
            port = input(" >>  ")
            if port:
                print(f"MYSQL Port: {port}")
                return port.strip()


    @staticmethod
    def user_name():
        '''Set MYSQL User'''
        print("Enter the MYSQL User: \n")
        while True:
            user_name = input(" >>  ")
            if user_name:
                print(f"MYSQL User: {user_name}")
                return user_name.strip()


    @staticmethod
    def password():
        '''Set MYSQL Password'''
        print("Enter the MYSQL Password: \n")
        while True:
            password = input(" >>  ")
            if password:
                print(f"MYSQL Password: {password}")
                return password.strip()


    @staticmethod
    def data_base():
        '''Set MYSQL Database'''
        print("Enter the MYSQL Database: \n")
        while True:
            data_base = input(" >>  ")
            if data_base:
                print(f"MYSQL Database: {data_base}")
                return data_base.strip()


    @staticmethod
    def config_exists():
        '''Check if movies_list.json exists.'''
        main_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(main_path, "config.json")
        return os.access(config_path, os.R_OK)


    def edit_config(self):
        '''Edit config.json file.'''

        if not self.config_exists():
            self.config_create()
            sys.exit()

        while True:
            print("\nPrevious config.json found. What do you want to do?\n")
            print("1. Edit config file.")
            print("2. Start new config file.")
            print("3. View Current configuration.")
            print("4. Quit.\n")

            option = input(" >>  ")
            print()

            if not option or option == "4":
                print("Done...\n")
                sys.exit()

            elif option == "1":
                self.change()
                print("Done...\n")

            elif option == "2":
                os.remove(Path(f"{self.dir}/config.json"))
                self.config_create()
                sys.exit()

            elif option == "3":
                self.view_config()

            else:
                print("Input not valid. \n")


    def view_config(self):
        '''View Current Settings'''
        config_path = os.path.join(self.dir, "config.json")

        with open(config_path) as config:
            data = json.load(config)

        while True:
            print("\nCurrent Config Settings:\n")
            print("MySQL Server Address    :  " + data["server"])
            print("MySQL Server Port       :  " + str(data["port"]))
            print("MySQL Database User     :  " + data["user_name"])
            print("MySQL Database Password :  " + data["password"])
            print("MySQL Database          :  " + data["data_base"])
            print("\n\nWhat Would You Like To Do?\n")
            print("1. Edit config file.")
            print("2. Start new config file.")
            print("3. Quit.\n")

            option = input(" >>  ")
            print()

            if not option or option == "3":
                print("Done...\n")
                sys.exit()

            elif option == "1":
                self.change()
                print("Done...\n")

            elif option == "2":
                os.remove(Path(f"{self.dir}/config.json"))
                self.config_create()
                sys.exit()

            else:
                print("Input not valid. \n")
