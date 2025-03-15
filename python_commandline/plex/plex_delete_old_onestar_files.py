#!/usr/bin/env python3

from plexapi.server import PlexServer
import os
import sys
import time
import json
from datetime import date
from datetime import datetime

# Target directory to search within (this is now a starting point)
#TARGET_DIR = "z:/video/"

# Number of days for the age check
DAYS_OLD = 400
# ratings are X2 for 5 stars, 4.0=2 stars
STAR_RATING=4.0
RESERVED_SECTIONS = ["dance", "drone"]

def main():
    """Finds all files in Plex libraries that are within the target directory or its subdirectories."""
    with open('plex_credentials.json') as json_file:
        try:
            plex_cred = json.load(json_file)
            # plex = PlexServer(PLEX_URL, PLEX_TOKEN)
            plex = PlexServer(plex_cred['baseurl'], plex_cred['token'])

            # Sections are different libraries, handle each differently
            for section in plex.library.sections():
                if section.title.lower() in RESERVED_SECTIONS:
                    print(f"Skipping reserved section:{section.title}")
                    continue
                if section.type == "show":
                    deleteShows(section)
                elif section.type == "movie":
                    deleteMovies(section)
                elif section.type == "song":
                    deleteSongs(section)
                    #print(f"section type: {section.type}")

        except Exception as e:
            print(f"Plex connection or other error: {e}")




def deleteSongs(songs):
    print("TODO: songs")

#tested working - 2025-02-10
def deleteMovies(movies):
    for movie in movies.all(): # Iterate through all items in the library
        try:
            if movie.viewCount>0:
                print(f"rating:{movie.userRating}   lastviewed: {movie.lastViewedAt} watchcount: {movie.viewCount} file:{movie.media[0].parts[0].file}")
                if normalizeUserRatingToTen(movie.userRating) <= STAR_RATING and showIsOld(movie.lastViewedAt,movie.viewCount):
                    print(f"DELETING {movie.userRating}  {movie.media[0].parts[0].file}")
                    movie.delete()
        except Exception as eBadType:
                print(f"deleteMovies: error: {eBadType}")

#tested working - 2025-02-10       
def deleteShows(shows):
    for show in shows.all(): # Iterate through all items in the library
        try:
            if show.viewCount > 0:
                print(f"rating:{show.userRating} viewcount:{show.viewCount} lastviewed:{show.lastViewedAt} {show.locations}")
                if normalizeUserRatingToTen(show.userRating) <= STAR_RATING and showIsOld(show.lastViewedAt,show.viewCount):
                    print(f"DELETING: {show.locations[0]}")
                    show.delete()
        except Exception as eBadType:
                print(f"deleteShows: error: {eBadType}")
                break





def showIsOld(lastViewedDate, numTimesViewed):
    #keep it for DAYS_OLD for each numTimesViewed (more popular shows kept longer)
    if lastViewedDate is None:
        #print("showIsOld:not viewed")
        return false
    if numTimesViewed is None or numTimesViewed < 1:
        #print("showIsOld:not viewed is zero")
        return false
    current_date = datetime.combine(date.today(), datetime.min.time())
    age = (current_date-lastViewedDate).days
    #print(f"showIsOld: last viewed {age}>{DAYS_OLD} days F/F: {(age > DAYS_OLD)}")
    return (age > DAYS_OLD)

def normalizeUserRatingToTen(value):
    if value is None or not isinstance(value, float):
        return 10
    return value






if __name__ == "__main__":
    main()



"""
if __name__ == "__main__":
    plex_files = get_plex_files(TARGET_DIR)

    for filepath in plex_files:
        print(f"Found a one star: {filepath}")



def delete_file(filepath):
    #Deletes the given file
    try:
        os.remove(filepath)
        print(f"Deleted: {filepath}")
    except OSError as e:
        print(f"Error deleting {filepath}: {e}", file=sys.stderr)
        return False

def modify_timestamp(filepath):
    #Modifies the timestamp of the file to the current time
    try:
        now = time.time()
        os.utime(filepath, (now, now))
        print(f"Modified timestamp: {filepath}")
    except OSError as e:
        print(f"Error modifying timestamp of {filepath}: {e}", file=sys.stderr)
        return False


print(f"Failed to delete {filepath}")
        if is_file_old(filepath):
            #modify_timestamp(filepath)
            if delete_file(filepath):
                continue
            else:
                print(f"Failed to delete {filepath}", file=sys.stderr)
        else:
            print(f"File {filepath} is a 1-star rating but not older than {DAYS_OLD} days. Skipping.")
            
                    #availableFields = [f.key.split('.')[-1] for f in  section.listFields()]
                    #print("Available fields:", availableFields)
            
            
            
            for section in plex.library.sections():
                if section.type == "movie":
                    print(f"{section}")
            return plex_files
 #MOVIES       


        except Exception as e:
            print(f"Plex connection or other error: {e}", file=sys.stderr)
            return plex_files
"""










