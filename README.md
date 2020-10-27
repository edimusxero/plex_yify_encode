# plex_yify_encode
Python3 script for searching and re encoding files larger than a givin size using FFMPEG and similar YIFY compression settings.


Usuage
 - python convert.py -s <source directory to crawl> -d <destination directory for converted files> -z <minimum file size either in G|g or M|m> -x path of database file
  
Database file will keep track of files you have already processed and will be created upon first run as well as the required tables
