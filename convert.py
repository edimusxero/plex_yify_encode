#!/usr/bin/python3
"""Python Script For FFMPEG File Encoding"""

import os
import sys
import subprocess
import sqlite3
import argparse

from sqlite3 import Error

PARSER = argparse.ArgumentParser(description='FFMPEG Plex File Conversion')
PARSER.add_argument('-s', '--source', type=str, required=True,
                    metavar='Path of Source Files')

PARSER.add_argument('-d', '--destination', type=str, required=True,
                    metavar='Destination for Converted Files')

PARSER.add_argument('-z', '--size', type=str, required=True,
                    metavar='File Size to Parse in Bytes')

PARSER.add_argument('-x', '--database', type=str, required=True,
                    metavar='Database File Location')

ARGS = PARSER.parse_args()

SOURCE = ARGS.source
DESTINATION = ARGS.destination
SIZE = ARGS.size
DATABASE = ARGS.database


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


def create_connection(db_file):
    """Creates connection to the database"""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as error:
        print(error)

    return conn


def create_table(conn, create_table_sql):
    """Creates Connection to the Table"""
    try:
        connection = conn.cursor()
        connection.execute(create_table_sql)
    except Error as error:
        print(error)


def convert_file(root, file):
    """Builds to the command to the FFMPEG File Conversion"""
    src = os.path.join(root, file)
    dest = os.path.join(DESTINATION, file)

    try:
        subprocess.call(['ffmpeg',
                         '-i',
                         src,
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
    except Error as error:
        print(error)
        sys.exit()

def check_table(database):
    """Checks whether the table exists and creats it if needed"""
    create_plex_table = """CREATE TABLE IF NOT EXISTS plex_files (
                                        id INTEGER PRIMARY KEY,
                                        name TEXT NOT NULL,
                                        size BIGINT
                                    );"""

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, create_plex_table)
    else:
        print("Error! cannot create the database connection.")

    return conn


def main():
    """Main program call"""
    database = os.path.join(DATABASE, 'plex.db')

    conn = check_table(database)
    cur = conn.cursor()

    for root, _, files in os.walk(SOURCE):
        for name in files:
            if name.endswith((".avi", ".mkv", ".mpeg", ".mp4", ".mpg")):
                size = os.path.getsize(os.path.join(root, name))
                cur.execute("SELECT id FROM plex_files WHERE name = ?", (name,))
                result = cur.fetchone()

                if result:
                    plex_id = result[0]
                    cur.execute("SELECT size FROM plex_files WHERE id = ?", (plex_id,))
                    result = cur.fetchone()
                    file_size = result[0]

                    if file_size > size:
                        print("Converting to a Smaller file " + name)
                        cur.execute("UPDATE plex_files SET size = (?) \
                                     WHERE name = (?)", (size, name))
                        conn.commit()
                else:
                    cur.execute("INSERT INTO plex_files(name, size) VALUES (?, ?)", (name, size))
                    conn.commit()
                    if size > size_conversion(SIZE):
                        print("Converting -- " + name)
                        convert_file(root, name)
    print("Processing Complete!")
    cur.close()

if __name__ == "__main__":
    main()