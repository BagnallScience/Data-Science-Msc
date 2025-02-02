import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import ipywidgets as widgets
from IPython.display import display, clear_output

class Top5ArtistsAnalyzer:
    def __init__(self, database_path):
        self.database_path = database_path
        
    def connect_to_database(self):
        try:
            return sqlite3.connect(self.database_path)
        except sqlite3.Error as e:
            print(f"❌ Database connection failed: {e}")
            return None

    def get_artist_data(self, conn, start_year, end_year):
        query = """
        SELECT 
            Artist.ArtistName AS Artist,  
            Song.Year AS Year,
            COUNT(Song.ID) AS Song_Count,  
            AVG(Song.Popularity) AS Avg_Popularity
        FROM Song
        INNER JOIN Artist ON Song.ArtistID = Artist.ID
        WHERE Song.Year BETWEEN ? AND ?
        GROUP BY Artist.ArtistName, Song.Year
        """
        return pd.read_sql_query(query, conn, params=(start_year, end_year))

    def calculate_rankings(self, df):
        df["Rank_Value"] = (df["Song_Count"] * 0.3) + (df["Avg_Popularity"] * 0.7)
        avg_rank_per_artist = df.groupby("Artist")["Rank_Value"].mean().sort_values(ascending=False)
        return avg_rank_per_artist.head(5).index.tolist()

    def highlight_top_artist(self, data):
        is_max = data == data.max()
        return ['background-color: #90EE90' if v else '' for v in is_max]  # Green highlight

    def format_output(self, df_top_5, start_year, end_year):
        pivot_df = df_top_5.pivot_table(
            index="Artist",
            columns="Year",
            values="Rank_Value",
            aggfunc="first"
        )
        
        pivot_df["Average"] = pivot_df.mean(axis=1)
        pivot_df = pivot_df.sort_values("Average", ascending=False)

        if "Average" in pivot_df.columns:
            pivot_df = pivot_df.drop("Average", axis=1)  
        if "Average" in pivot_df.index:
            pivot_df = pivot_df.drop("Average", axis=0)  

        styled_df = pivot_df.style\
            .set_properties(**{
                'background-color': '#f5f5f5',
                'border': '1px solid #cccccc',
                'padding': '8px',
                'text-align': 'center'
            })\
            .set_table_styles([
                {'selector': 'thead',
                 'props': [('background-color', '#2c3e50'),
                          ('color', 'white'),
                          ('font-weight', 'bold'),
                          ('text-align', 'center')]},
                {'selector': 'th.row_heading',
                 'props': [('background-color', '#34495e'),
                          ('color', 'white'),
                          ('font-weight', 'bold'),
                          ('text-align', 'left')]},
            ])\
            .apply(self.highlight_top_artist, axis=0)\
            .format(lambda x: f'{x:.2f}' if pd.notnull(x) else 'Null')

        display(styled_df)

    def plot_rankings(self, df_top_5, avg_rank_per_year, start_year, end_year):
        plt.figure(figsize=(12, 8))
        
        colors = plt.cm.Set2(np.linspace(0, 1, len(df_top_5["Artist"].unique())))
        for artist, color in zip(df_top_5["Artist"].unique(), colors):
            artist_data = df_top_5[df_top_5["Artist"] == artist]
            plt.plot(artist_data["Year"], artist_data["Rank_Value"], '-o', 
                    label=artist, color=color, linewidth=2, markersize=8)

        plt.plot(avg_rank_per_year["Year"], avg_rank_per_year["Rank_Value"], 
                'k--', label="Average", linewidth=2)
        
        plt.title(f"Top 5 Artists Rankings ({start_year}-{end_year})", fontsize=14, pad=20)
        plt.xlabel("Year", fontsize=12)
        plt.ylabel("Rank Value", fontsize=12)
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend(title="Artists", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()

    def top_5_artists(self, start_year, end_year):
        conn = self.connect_to_database()
        if not conn:
            return

        try:
            raw_data = self.get_artist_data(conn, start_year, end_year)
            if raw_data.empty:
                print(f"⚠ No data available for {start_year}–{end_year}")
                return

            top_artists = self.calculate_rankings(raw_data)
            df_top_5 = raw_data[raw_data["Artist"].isin(top_artists)].copy()
            df_top_5["Rank_Value"] = (df_top_5["Song_Count"] * 0.3) + (df_top_5["Avg_Popularity"] * 0.7)
            
            avg_rank_per_year = df_top_5.groupby("Year")["Rank_Value"].mean().reset_index()

            self.format_output(df_top_5, start_year, end_year)

            # Add spacing between table and graph
            display(widgets.HTML("<br><br><br>"))  

            self.plot_rankings(df_top_5, avg_rank_per_year, start_year, end_year)

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    database_path = "CWDatabase.db"
    analyzer = Top5ArtistsAnalyzer(database_path)
    
    try:
        start_year = int(input("Enter start year (1998-2020): "))
        end_year = int(input("Enter end year (1998-2020): "))
        
        if 1998 <= start_year <= 2020 and 1998 <= end_year <= 2020 and start_year <= end_year:
            analyzer.top_5_artists(start_year, end_year)
        else:
            print("⚠ Please enter valid years between 1998 and 2020")
    except ValueError:
        print("⚠ Please enter valid numeric years")
