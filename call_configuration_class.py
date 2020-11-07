#!/usr/bin/python3
'''Configuration Call Class'''

import os
import sys
import json
from pathlib import Path
import argparse
import pymysql
from config_generator import ConfigJSON


class CallConfig(argparse.Action):
    '''Config File Class'''
    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in "-x, --schema":
            print("It's schema time!")
            sys.exit()
        else:
            ConfigJSON().edit_config()


    @staticmethod
    def create_database_connection():
        '''Function for creating the db connection'''
        dir_path = Path(f"{os.path.dirname(os.path.abspath(__file__))}"
                        "/config.json")

        if os.path.exists(dir_path):
            with open(dir_path) as config:
                data = json.load(config)

            try:
                conn = pymysql.connect(host = data["server"],
                                    port = int(data["port"]),
                                    user = data["user_name"],
                                    password = data["password"],
                                    db = data["data_base"]
                                    )

            except pymysql.OperationalError as op_error:
                print(op_error)
                sys.exit()

            return conn

        print("\nMissing config file.  Creating now\n")
        ConfigJSON().config_create()
        sys.exit()
