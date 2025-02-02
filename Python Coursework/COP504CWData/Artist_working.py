import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ipywidgets as widgets
from IPython.display import display, clear_output

class ArtistPopularityAnalyzer:
    """Analyzes an artist's popularity across different music genres."""

    def __init__(self, database_path):
        self.database_path = database_path

    def connect_db(self):
        """Establishes a connection to the SQLite database."""
        try:
            conn = sqlite3.connect(self.database_path)
            return conn
        except sqlite3.Error as e:
            print(f"❌ Database connection failed: {e}")
            return None

    def check_artist_exists(self, artist_name):
        """Checks if an artist exists in the database."""
        query = """
        SELECT DISTINCT Artist.ArtistName 
        FROM Song 
        INNER JOIN Artist ON Song.ArtistID = Artist.ID
        WHERE LOWER(Artist.ArtistName) = LOWER(?)
        """
        with self.connect_db() as conn:
            if conn is None:
                return False  # Database connection failed
            result = pd.read_sql_query(query, conn, params=(artist_name,))
        return not result.empty

    def get_artist_popularity(self, artist_name):
        """Fetches the artist's average popularity per unique genre."""
        query = """
        SELECT Genre.Genre AS Genre, AVG(Song.Popularity) AS Popularity
        FROM Song
        INNER JOIN Genre ON Song.GenreID = Genre.ID
        INNER JOIN Artist ON Song.ArtistID = Artist.ID
        WHERE LOWER(Artist.ArtistName) = LOWER(?)
        AND Genre.Genre NOT LIKE '%/%'  
        AND Genre.Genre NOT LIKE '%&%'  
        GROUP BY Genre.Genre
        """
        with self.connect_db() as conn:
            return pd.read_sql_query(query, conn, params=(artist_name,))

    def get_all_genre_popularity(self):
        """Fetches the average popularity across all pure genres."""
        query = """
        SELECT Genre.Genre, AVG(Song.Popularity) AS "Genre Popularity"
        FROM Song
        INNER JOIN Genre ON Song.GenreID = Genre.ID
        WHERE Genre.Genre NOT LIKE '%/%'  
        AND Genre.Genre NOT LIKE '%&%'
        AND Genre.Genre IN ('rock', 'metal', 'blues', 'jazz', 'pop', 'hip hop', 'country', 'classical', 'electronic')
        GROUP BY Genre.Genre
        """
        with self.connect_db() as conn:
            return pd.read_sql_query(query, conn)

    def analyze_artist(self, artist_name):
        """Analyzes an artist's popularity across genres and visualizes the results."""
        clear_output(wait=True)
        if not self.check_artist_exists(artist_name):
            print(f"⚠️ No data found for artist '{artist_name}'. Please try another name.")
            return

        artist_data = self.get_artist_popularity(artist_name)

        if artist_data.empty:
            print(f"⚠️ No genre-specific data found for artist '{artist_name}'.")
            return

        all_genre_data = self.get_all_genre_popularity()
        if all_genre_data.empty:
            print("⚠️ No data available for genre popularity.")
            return

        merged_data = pd.merge(all_genre_data, artist_data, on="Genre", how="left")
        merged_data["Popularity"] = pd.to_numeric(merged_data["Popularity"], errors="coerce")
        merged_data["Genre Popularity"] = pd.to_numeric(merged_data["Genre Popularity"], errors="coerce")
        merged_data.fillna(0, inplace=True)

        # Set index starting from 1 instead of 0
        merged_data.index = merged_data.index + 1  

        self.display_professional_table(merged_data)

        # Visualize the data
        self.visualize_data(merged_data)

    def display_professional_table(self, df):
        """Formats and displays a dataframe with professional styling and highlights only when popularity overlaps the artist's main genre."""
        def highlight_row(row):
            if row["Popularity"] > row["Genre Popularity"] and row["Genre Popularity"] > 0:
                return ['background-color: #90EE90'] * len(row)  # Light green highlight only if the genre exists
            return [''] * len(row)

        styled_df = df.style.set_table_styles(
            [
                {'selector': 'th', 'props': [('background', '#40466e'), ('color', 'white'), ('font-weight', 'bold'), ('text-align', 'center')]},
                {'selector': 'td', 'props': [('text-align', 'center'), ('padding', '5px')]},
                {'selector': 'tr:nth-child(even)', 'props': [('background', '#f2f2f2')]},
                {'selector': 'tr:hover', 'props': [('background', '#ddd')]}
            ]
        ).format(
            {'Genre Popularity': "{:.2f}", 'Popularity': "{:.2f}"}
        ).apply(highlight_row, axis=1)  # Apply row-wise highlighting

        display(styled_df)

    def visualize_data(self, df):
        """Creates a bar chart comparing artist popularity to genre popularity."""
        if df.empty:
            print("⚠️ No data available for visualization.")
            return

        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.arange(len(df))
        width = 0.3

        ax.bar(x - width, df["Popularity"], width, label="Artist Popularity", color='skyblue')
        ax.bar(x, df["Genre Popularity"], width, label="Genre Popularity", color='orange')

        ax.set_xticks(x)
        ax.set_xticklabels(df["Genre"], rotation=45)
        ax.set_ylabel("Popularity Score")
        ax.set_title("Artist Popularity vs. Genre Popularity")
        ax.legend()
        plt.tight_layout()
        plt.show()

# Initialize the analyzer
database_path = "CWDatabase.db"
analyzer = ArtistPopularityAnalyzer(database_path)

# **Artist Input Widgets** (Initially Hidden)
artist_widget = widgets.Text(
    placeholder="Enter artist name...",
    description="Artist:",
    layout=widgets.Layout(width="50%"),
    visible=False  # Initially hidden
)
artist_submit_button = widgets.Button(description="Analyze Artist", style={'button_color': "#FFA500"}, visible=False)

output_area = widgets.Output()

# Function to reveal artist input box
def show_artist_input(b):
    artist_widget.visible = True  # Make artist input visible
    artist_submit_button.visible = True  # Make submit button visible

# Function to trigger the artist analysis
def on_button_click(b):
    with output_area:
        clear_output(wait=True)
        analyzer.analyze_artist(artist_widget.value)

# Bind the button to the relevant function
artist_submit_button.on_click(on_button_click)

# Display a button to show the artist input box
reveal_button = widgets.Button(description="Enter Artist Name", style={'button_color': "#FFA500"})
reveal_button.on_click(show_artist_input)

# Display widgets
display(reveal_button, artist_widget, artist_submit_button, output_area)