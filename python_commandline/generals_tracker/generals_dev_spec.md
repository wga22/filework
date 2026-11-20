
database tables
    Design a data schema that includes two tables.
    users:
        row_id
        user_name
        handle
        last_seen
        
    sessions
        row_id
        user_row_id
        start_time
        end_time
        duration

python application
    update "generalsplayersonline.py" to support JSON and POSTGRES.
    JSON
        load the generals_dev_spec.json
        "Players": each time running, sychronize data from the generals_dev_spec.json "Players" node to the users table.
        "postgres": use "postgres" to store database credentials
        "thingspeak": just a placeholder for now


    POSTGRES
        in addition to displaying matches, also insert matches into the database.
        create a function that does the database work, immediately after the line "players = fetch_and_parse_players()" in main()
        search the PLAYERS_URL (https://www.playgenerals.online/players) for matches against any of the handles in the user table.  
        For each match, determine if this is an extension of the previous session or a new session.  
        Extended session:
            definition: The session is an extension if the previous time searching, the user was online. 
            action: update the prior session row by increasing the duration.
            action: update the user's row "last_seen" with current timestamp
        New session: if this is the first view of the handle, then
        Close old sessions:
            for each of the users that were seen in the last cycle, but not in this cycle, update their sessions "end_time" to be the timestamp of the previous search.
            
            
            
PHP page
    write a php page, that uses the apache environment variables listed below.
        SetEnv CHAMFOX_DB_HOST "spiderman"
        SetEnv CHAMFOX_DB_PORT "5432"
        SetEnv CHAMFOX_DB_NAME "chamfox"
        SetEnv CHAMFOX_DB_USER "will"
        SetEnv CHAMFOX_DB_PASS "XXXXXXX"
        
     The page should include the following informstion:
     1) who is currently online
     2) statistics for the players (rolled up by user.user_name)
        - date last seen online
        - current session duration when online
        - playtime over the last 24 hours
        - playtime, per day, for each of the last 7 days
        - average daily playtime over last 60 days
        - playtime, per month, for the last 12 months
            