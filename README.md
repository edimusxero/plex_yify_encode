# plex_yify_encode
Python3 script for searching and re encoding files larger than a givin size using FFMPEG and similar YIFY compression settings.


Usuage
 - python convert.py -i (source directory to crawl) -d (destination directory for converted files) -s (minimum file size either in G|g or M|m) [-c for database file configuration]
  
Database file will keep track of files you have already processed and will be created upon first run as well as the required tables


Requires FFMPEG to work properly.  This has only been tested on Ubuntu 18+ using Python 3.8
 - This will now install FFMEPG in ubuntu upon initial run if the package is missing


** Requires MySQL database.  I was running into issue with multiple runs of the script using sqlite due to database file locking and instead of rewriting and reworking it to make sqllite3 work with multiple connections I went with what I know and chose MySQL



