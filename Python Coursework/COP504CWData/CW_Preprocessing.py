import pandas as pd
import sqlite3

class PreprocessingManager:
    """
    A class to manage song data preprocessing and SQLite database operations.
    """

    def __init__(self, db_path="CWDatabase.db"):
        """
        Initializes the database manager with the SQLite database path.
        """
        self.db_path = db_path

    def create_database_structure(self):
        """
        Creates tables for Artist, Genre, and Song in the SQLite database.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.executescript("""
            CREATE TABLE IF NOT EXISTS Artist (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ArtistName TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Genre (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Genre TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS Song (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Song TEXT NOT NULL,
                Duration INTEGER NOT NULL,
                Explicit BOOLEAN NOT NULL,
                Year INTEGER NOT NULL,
                Popularity INTEGER NOT NULL,
                Danceability REAL NOT NULL,
                Speechiness REAL NOT NULL,
                ArtistID INTEGER NOT NULL,
                GenreID INTEGER NOT NULL,
                FOREIGN KEY (ArtistID) REFERENCES Artist(ID) ON DELETE CASCADE,
                FOREIGN KEY (GenreID) REFERENCES Genre(ID) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_artist ON Song (ArtistID);
            CREATE INDEX IF NOT EXISTS idx_genre ON Song (GenreID);
            """)

            conn.commit()
            print("✅ Database structure successfully created.")
        except sqlite3.Error as e:
            print(f"❌ Database Error: {e}")
        finally:
            conn.close()

    def preprocess_data(self, df):
        """
        Cleans and processes a song dataset.
        - Converts duration from milliseconds to seconds.
        - Splits multi-genre songs into separate rows.
        - Filters based on predefined criteria.

        Args:
            df (pd.DataFrame): The raw dataset.

        Returns:
            pd.DataFrame: The cleaned and processed dataset.
        """
        try:
            required_columns = {"song", "duration_ms", "explicit", "year", "popularity", "danceability", "speechiness", "artist", "genre"}
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                raise ValueError(f"❌ Missing required columns: {missing}")

            # Convert duration from milliseconds to seconds
            df = df.copy()  # ✅ Prevents `SettingWithCopyWarning`
            df.rename(columns={"duration_ms": "duration"}, inplace=True)
            df["duration"] = (df["duration"] / 1000).round().astype(int)

            # Apply filters
            df = df[
                (df["popularity"] > 50) & 
                (df["speechiness"].between(0.33, 0.66)) & 
                (df["danceability"] > 0.20)
            ].copy()  # ✅ Ensures modification happens on a new DataFrame

            # ✅ Fix: Use `.loc` to safely modify genre column
            df.loc[:, "genre"] = df["genre"].str.split(', ')

            # Expand genres into separate rows
            df = df.explode("genre").reset_index(drop=True)

            print(f"✅ Preprocessing complete. {len(df)} records remain after filtering and genre expansion.")
            return df

        except ValueError as ve:
            print(f"❌ Data Processing Error: {ve}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")

        return pd.DataFrame()

    def populate_database(self, df):
        """
        Populates the SQLite database with processed song data.

        Args:
            df (pd.DataFrame): The cleaned dataset.
        """
        try:
            if df.empty:
                print("⚠ No data available to insert. Aborting process.")
                return

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert unique artists and genres
            unique_artists = df[['artist']].drop_duplicates()
            unique_genres = df[['genre']].drop_duplicates()

            cursor.executemany("INSERT OR IGNORE INTO Artist (ArtistName) VALUES (?)", unique_artists.values)
            cursor.executemany("INSERT OR IGNORE INTO Genre (Genre) VALUES (?)", unique_genres.values)
            conn.commit()

            print(f"✅ Inserted {len(unique_artists)} unique artists and {len(unique_genres)} unique genres.")

            # Map Artist and Genre IDs
            artist_id_map = {name: idx for idx, name in pd.read_sql("SELECT ID, ArtistName FROM Artist", conn).values}
            genre_id_map = {name: idx for idx, name in pd.read_sql("SELECT ID, Genre FROM Genre", conn).values}

            # Insert Songs with Artist and Genre mappings
            song_records = []
            for _, row in df.iterrows():
                artist_id = artist_id_map.get(row["artist"])
                genre_id = genre_id_map.get(row["genre"])

                if artist_id and genre_id:
                    song_records.append((
                        row["song"], row["duration"], row["explicit"], row["year"],
                        row["popularity"], row["danceability"], row["speechiness"],
                        artist_id, genre_id
                    ))

            cursor.executemany("""
                INSERT INTO Song (Song, Duration, Explicit, Year, Popularity, Danceability, Speechiness, ArtistID, GenreID)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, song_records)

            conn.commit()
            print(f"✅ Inserted {len(song_records)} song-genre records into the database.")

        except sqlite3.Error as e:
            print(f"❌ Database Insertion Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
        finally:
            conn.close()

    def import_new_data(self, df):
        """
        Imports a new dataset and updates the database.

        Args:
            df (pd.DataFrame): The new dataset.
        """
        print("📂 Importing New Dataset...")
        df = self.preprocess_data(df)
        self.create_database_structure()
        self.populate_database(df)

    def show_available_genres(self):
        """
        Fetches and displays all unique genres in the database.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            query = "SELECT Genre FROM Genre ORDER BY Genre ASC"
            genres = pd.read_sql_query(query, conn)
            conn.close()

            if genres.empty:
                print("⚠ No genres found in the database.")
            else:
                print("\n🎵 Available Genres:")
                print(genres.to_string(index=False))  # Display genres in console

        except sqlite3.Error as e:
            print(f"❌ Database Query Error: {e}")

    def integrate_new_data(self, df):
        """
        Integrates new data into the system by preprocessing and populating the database.
        
        Args:
            df (pd.DataFrame): The new song dataset.
        """
        # Preprocess the data
        print("📂 Integrating New Data into the Database...")
        df = self.preprocess_data(df)
        
        # Ensure database structure is created before inserting data
        self.create_database_structure()

        # Populate the database with the new data
        self.populate_database(df)

        print("✅ New data successfully integrated into the database!")

# --- Execution Block ---
if __name__ == "__main__":
    db_manager = PreprocessingManager(db_path="CWDatabase.db")

    print("\n🚀 Starting Data Processing & Database Setup...")
    db_manager.create_database_structure()

    # Load initial data from 'songs.csv'
    try:
        df = pd.read_csv("songs.csv")
        db_manager.integrate_new_data(df)  # Use the new integrate_new_data method
    except FileNotFoundError:
        print("⚠ No 'songs.csv' file found. Please upload a dataset manually.")

    print("\n📌 Fetching available genres in the database...")
    db_manager.show_available_genres()

    print("\n🎉 Database setup completed successfully!")
