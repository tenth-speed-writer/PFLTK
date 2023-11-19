import sqlite3
import typing
import datetime
import asyncio

class DB:
    @staticmethod
    def format_date_for_db(dt: datetime.datetime) -> str:
        """
        Converts a datetime into an ISO8601 string (eg "YYYY-MM-DD HH:MM:SS.etc").
        Included in the DB module because SQLite doesn't have a native date format.

        Args:
            dt (datetime.datetime): The datetime to be converted

        Returns:
            str: The ISO8601 formatting of the provided string
        """
        
        return dt.isoformat()
    
    @staticmethod
    def format_date_from_db(dt: str) -> datetime.datetime:
        """
        Converts an ISO8601 string (eg "YYYY-MM-DD HH:MM:SS.etc") into a Python
        datetime object, working around SQLite's lack of datetime values.

        Args:
            dt (str): A datetime represented as an ISO8601 formatted string

        Returns:
            datetime.datetime: A datetime object corresponding to the provided string
        """
        return datetime.datetime.fromisoformat(str)

    def get_connection(self) -> sqlite3.Connection:
        """
        Generates a new SQLite3 connection object based on
        the connection string provided at instantiation.

        Returns:
            sqlite3.Connection: A SQLite3 connection object, based on the given string
        """
        return sqlite3.connect(self.connection_string)
    
    def generate_db(self) -> None:
        """
        Used to create the database file, if necessary, at instantiation.

        The schema lives here.
        """
        creation_sql = """
            /*
            Represents a single war on the server for which this application
            has been set up. Used primarily to distinguish maps and the
            things associated with them as unique across wars.
            */
            CREATE TABLE IF NOT EXISTS wars (
                war_number INTEGER PRIMARY KEY NOT NULL,
                last_fetched_on TEXT NOT NULL
            );

            /*
            Represents a single hex tile on the strategic map by
            its name and the unique war in which it occurred.
            */
            CREATE TABLE IF NOT EXISTS maps (
                map_name TEXT NOT NULL,
                war_number INTEGER NOT NULL,
                
                CONSTRAINT pk_maps
                PRIMARY KEY (
                    map_name,
                    war_number
                ),

                CONSTRAINT fk_map_war
                FOREIGN KEY (war_number)
                REFERENCES wars (war_number)
                ON UPDATE CASCADE
                ON DELETE CASCADE
            );

            /*
            Represents a major map label, of the kind used to distinguish the
            individual sub-zones within each hex. Since map location data
            doesn't include this value, we need to infer the closest major
            label to a given map point of interest based on distance.

            Distance is given here in terms of relative map
            dimension from a given hex's topographic origin,
            and follows typical Euclidean distance.

            Since these are associated uniquely with the maps table, they're
            unique to a given hex in a given war at a unique x and y position.
            */
            CREATE TABLE IF NOT EXISTS major_labels (
                map_name TEXT NOT NULL,
                war_number INTEGER NOT NULL,
                label TEXT NOT NULL,

                x REAL NOT NULL,
                y REAL NOT NULL,

                CONSTRAINT pk_labels
                PRIMARY KEY (
                    map_name,
                    war_number,
                    label
                ),

                CONSTRAINT fk_label_map_name
                FOREIGN KEY (
                    map_name,
                    war_number
                )
                REFERENCES maps (
                    map_name,
                    war_number
                )
                ON UPDATE CASCADE
                ON DELETE CASCADE
            );

            /*
            Essentially a codebook table for the 'icon_type' variable
            of the 'icons' table. Should be populated from the file
            'icon_codebook.csv' when the database is created, and
            that file in turn maintained between game versions.
            */
            CREATE TABLE IF NOT EXISTS icon_type_names (
                icon_id INTEGER PRIMARY KEY,
                icon_text TEXT NOT NULL
            );

            /*
            Represents a single map icon as it exists or existed on a particular
            hex, at a particular x and y location, during a particular war.

            In short, this is a unique location one might deliver to or from.

            Since the API doesn't share specific site IDs or the unique sub-hex zone
            in which sites occur, the best we can do is use their x and y positions
            (given in term of relative map dimensions) to find their closest
            associated major label on the map.

            This allows us to be as specific as "the Relic Base near Loggerhead"
            or "the Storage Depot near The Abandoned Ward" when describing origin
            points and destinations for logistics tickets. Not ideal, but it's
            close enough to get people on task.
            */
            CREATE TABLE IF NOT EXISTS icons (
                map_name TEXT NOT NULL,
                war_number INTEGER NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,

                icon_type INTEGER NOT NULL,

                CONSTRAINT pk_icons
                PRIMARY KEY (
                    map_name,
                    war_number,
                    x,
                    y
                ),

                CONSTRAINT fk_icon_map_name
                FOREIGN KEY (
                    map_name,
                    war_number
                )
                REFERENCES maps (
                    map_name,
                    war_number
                )
                ON UPDATE CASCADE
                ON DELETE CASCADE
            );

            /*
            Represents a single hauling or touch task managed by the ticker.

            Associated with a specific destination and an optional origin.
            A procurement order, for instance, has a destination but no origin.
            A delivery order would have both a destination and an origin, and a
            mine touch/refueling order would have the same origin and destination.
            */
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_number INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                war_number INT NOT NULL,

                destination_map_name TEXT NOT NULL,
                destination_x REAL NOT NULL,
                destination_y REAL NOT NULL,
                destination_description TEXT,

                origin_map_name TEXT,
                origin_x REAL,
                origin_y REAL,
                origin_description TEXT,

                objective_description TEXT NOT NULL,
                created_on TEXT NOT NULL,

                CONSTRAINT fk_ticket_destination_map
                FOREIGN KEY (
                    destination_map_name,
                    war_number,
                    destination_x,
                    destination_y
                )
                REFERENCES icons (
                    map_name,
                    war_number,
                    x,
                    y
                )
                ON UPDATE CASCADE
                ON DELETE CASCADE,

                CONSTRAINT fk_ticket_origin_map
                FOREIGN KEY (
                    origin_map_name,
                    war_number,
                    origin_x,
                    origin_y
                )
                REFERENCES icons (
                    map_name,
                    war_number,
                    x,
                    y
                )
                ON UPDATE CASCADE
                ON DELETE CASCADE
            );


        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(creation_sql)
        conn.commit()
        conn.close()
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
