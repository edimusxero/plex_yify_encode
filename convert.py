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


def get_length(filename):
    """Returns the length of the media file"""
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True)

    length_in_seconds = float(result.stdout)

    return str(round(length_in_seconds / 60, 2))


def test_completion(src_file, dest_file, file_name):
    """Tests Length Of The Converted File to Ensure Completion"""
    if src_file == dest_file:
        try:
            sql_query = "UPDATE compressed_files\
                        SET Response = (SELECT Id\
                        FROM assoc_process_response WHERE\
                        Response = 'Yes'),\
                        Processing = (SELECT Id\
                        FROM assoc_process_response WHERE\
                        Response = 'No')\
                        WHERE NAME = %s"

            CURSOR.execute(sql_query, (file_name))
            CONN.commit()
            return True

        except pymysql.OperationalError as op_error:
            print(op_error)
            CONN.rollback()
            return False

    return False


def convert_file(root, file):
    """Builds to the command to the FFMPEG File Conversion"""
    src = os.path.join(root, file)
    dest = os.path.join(DESTINATION, file)

    try:
        print("Converting -- " + file)
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

        return test_completion(get_length(src), get_length(dest), file)

    except RuntimeError as error:
        print(error)
        sql_query = "DELETE FROM compressed_files WHERE name = %s"
        CURSOR.execute(sql_query, file)
        os.remove(dest)
        return False


def process_files_for_compression(file_root, files_for_processing):
    '''Main function for processing the file compression and database entries'''
    for name in files_for_processing:
        if name.endswith((".avi", ".mkv", ".mpeg", ".mp4", ".mpg")):
            size = os.path.getsize(os.path.join(file_root, name))
            sql_query = "SELECT Id FROM compressed_files WHERE name = %s"
            CURSOR.execute(sql_query, name)
            result = CURSOR.fetchone()

            if result is not None:
                plex_id = result[0]
                sql_query = "SELECT Size,\
                             (SELECT Response FROM assoc_process_response\
                             WHERE compressed_files.Response = Id) AS Response,\
                             (SELECT Response From assoc_process_response\
                             WHERE compressed_files.Processing = Id) AS Processing\
                             FROM compressed_files WHERE Id = %s"

                CURSOR.execute(sql_query, plex_id)
                result = CURSOR.fetchone()

                file_size = result[0]
                response = result[1]
                processing = result[2]

                if file_size > size and response == 'Yes' and processing == 'No':
                    print("Converting to a Smaller file " + name)
                    sql_query = "UPDATE compressed_files SET Size = %s WHERE name = %s"
                    CURSOR.execute(sql_query, (size, name))
                    CONN.commit()
                    continue

                if response == 'No' and processing == 'Yes':
                    print(name + " is currently processing")
                    continue

            else:
                if os.path.isfile(os.path.join(DESTINATION, name)):
                    print(name + " : exists and may be processing by a seperate server")
                    continue

                if size > size_conversion(SIZE):
                    try:
                        sql_query = "INSERT INTO compressed_files\
                                     (Name, Size, Response, Processing)\
                                     VALUES (%s, %s,\
                                     (SELECT Id FROM assoc_process_response WHERE\
                                     Response = 'No'),\
                                     (SELECT Id FROM assoc_process_response WHERE\
                                     Response = 'Yes'))"

                        CURSOR.execute(sql_query, (name, size))
                        CONN.commit()

                    except pymysql.OperationalError as op_error:
                        print(op_error)
                        CONN.rollback()

                    if convert_file(file_root, name):
                        print("File conversion successful")

                    else:
                        print("File conversion has failed")


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