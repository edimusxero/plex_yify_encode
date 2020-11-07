#!/usr/bin/python3
"""Python Script For FFMPEG File Encoding"""

import os
import sys
import subprocess
import argparse
import pymysql
import apt
from config_generator import ConfigJSON
from call_configuration_class import CallConfig


PARSER = argparse.ArgumentParser(description='FFMPEG Plex File Conversion')
PARSER.register('action', 'config', CallConfig)

CONVERSION = PARSER.add_argument_group('Conversion', 'Parameters for File Conversion')

CONVERSION = PARSER.add_argument('-i', '--source', required=True,
                    help='Path of Source Files')

CONVERSION = PARSER.add_argument('-d', '--destination', required=True,
                    help='Destination for Converted Files')

CONVERSION = PARSER.add_argument('-s', '--size', required=True,
                    help='File Size to Parse in Bytes')

CONFIGFILE = PARSER.add_argument_group('Config',
                                       ' - Configuration File for the MySQL Database')

CONFIGFILE.add_argument('-c', '--config', nargs=0,
                        action='config', help='Create or Edit Configuration File')

CONFIGFILE.add_argument('-x', '--schema', nargs=0,
                        action='config', help='Create Database and Schema')

ARGS = PARSER.parse_args()

SOURCE = ARGS.source
DESTINATION = ARGS.destination
SIZE = ARGS.size

CONN = CallConfig.create_database_connection()

CURSOR = CONN.cursor()


def check_package():
    """Installs missing linux packages if not present"""
    cache = apt.Cache()
    if not cache['ffmpeg'].is_installed:
        print("Installing FFMPEG")
        subprocess.call(['apt', 'install', 'ffmpeg', '-y'])


def size_conversion(file_size):
    """Conversion Function for the string size imput"""
    size_unit = file_size[-1]
    size = file_size[:-1]

    if size_unit in ('G', 'g'):
        return int(size) * 1073741824
    if size_unit in ('M', 'm'):
        return int(size) * 1048576

    print("Unknown Size Unit")
    sys.exit()


def convert_file(root, file):
    """Builds to the command to the FFMPEG File Conversion"""
    src = os.path.join(root, file)
    dest = os.path.join(DESTINATION, file)

    try:
        subprocess.call(['ffmpeg',
                         '-i',
                         src,
                         '-metadata',
                         'title=',
                         '-metadata',
                         'comment=',
                         '-vf',
                         'scale=-2:720',
                         '-crf',
                         '25',
                         '-vcodec',
                         'h264',
                         '-acodec',
                         'aac',
                         dest
                        ])
    except RuntimeError as error:
        print(error)
        sys.exit()


def process_files_for_compression(file_root, files_for_processing):
    '''Main function for processing the file compression and database entries'''
    for name in files_for_processing:
        if name.endswith((".avi", ".mkv", ".mpeg", ".mp4", ".mpg")):
            size = os.path.getsize(os.path.join(file_root, name))
            sql_query = "SELECT id FROM compressed_files WHERE name = %s"
            CURSOR.execute(sql_query, name)
            result = CURSOR.fetchone()

            if result is not None:
                plex_id = result[0]
                sql_query = "SELECT size FROM compressed_files WHERE id = %s"
                CURSOR.execute(sql_query, plex_id)
                result = CURSOR.fetchone()

                file_size = result[0]

                if file_size > size:
                    print("Converting to a Smaller file " + name)
                    sql_query = "UPDATE compressed_files SET size = %s WHERE name = %s"
                    CURSOR.execute(sql_query, (size, name))
                    CONN.commit()
                    continue


            else:
                if size > size_conversion(SIZE):
                    try:
                        sql_query = "INSERT INTO compressed_files(name, size) VALUES (%s, %s)"
                        CURSOR.execute(sql_query, (name, size))
                        CONN.commit()
                        print("Converting -- " + name)
                        convert_file(file_root, name)

                    except pymysql.OperationalError as op_error:
                        print(op_error)
                        CONN.rollback()


def main():
    """Main program call"""
    check_package()

    if not ConfigJSON().config_exists():
        msg = "\nThere was no config.json file so let's create one.\n"
        print(msg)
        ConfigJSON().config_create()
        sys.exit()

    for root, _, files in os.walk(SOURCE):
        process_files_for_compression(root, files)

    print("Processing Complete!")
    CURSOR.close()
    CONN.close()


if __name__ == "__main__":
    main()
