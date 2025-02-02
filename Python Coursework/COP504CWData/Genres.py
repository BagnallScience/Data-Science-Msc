import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ipywidgets as widgets
from IPython.display import display, clear_output

class GenreStatisticsAnalyzer:
    def __init__(self, database_path):
        self.database_path = database_path

    def connect_db(self):
        return sqlite3.connect(self.database_path)

    def validate_year(self, year):
        query = "SELECT DISTINCT Year FROM Song WHERE Year = ?;"
        with self.connect_db() as conn:
            result = pd.read_sql_query(query, conn, params=(year,))
        return not result.empty

    def fetch_genre_statistics(self, year):
        query = """
        SELECT 
            Genre.Genre AS Genre,  
            AVG(Song.Danceability) AS Avg_Danceability,
            COUNT(Song.ID) AS Total_Songs,
            AVG(Song.Popularity) AS Avg_Popularity,
            AVG(Song.Duration) AS Avg_Duration
        FROM Song
        INNER JOIN Genre ON Song.GenreID = Genre.ID
        WHERE Song.Year = ?
        GROUP BY Genre.Genre
        """
        with self.connect_db() as conn:
            df = pd.read_sql_query(query, conn, params=(year,))

        df["Genre"] = df["Genre"].astype(str).str.lower()
        df["Genre"] = (
            df["Genre"]
            .str.replace(r"[\{\}\[\]\(\)]", "", regex=True)
            .str.split(",").str[0]
            .str.strip()
            .str.title()
        )

        df = df[df["Genre"].str.lower() != "set"]
        df["Avg_Duration"] = df["Avg_Duration"] / 1000  # Convert duration to seconds

        return df

    def highlight_top_genre(self, data):
        is_max = data == data.max()
        return ['background-color: #90EE90' if v else '' for v in is_max]  

    def format_output(self, df, year):
        pivot_df = df.pivot_table(
            index="Genre",
            values=["Total_Songs", "Avg_Danceability", "Avg_Popularity", "Avg_Duration"],
            aggfunc="mean"
        )

        pivot_df.columns = [
            "Total Songs",
            "Average Duration (seconds)",
            "Average Popularity",
            "Average Danceability"
        ]

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
            .apply(self.highlight_top_genre, axis=0)\
            .format(lambda x: f'{x:.2f}' if pd.notnull(x) else 'Null')

        display(styled_df)

    def visualize_data(self, df, year):
        if df.empty:
            print(f"⚠ No unique genre data available for {year}. Try another year.")
            return

        df_unique = df.drop_duplicates(subset="Genre").copy()

        fig, ax = plt.subplots(figsize=(18, 16))  

        total = df_unique["Total_Songs"].sum()
        df_unique["Percentage"] = (df_unique["Total_Songs"] / total) * 100

        colors = plt.cm.Set3.colors if len(df_unique) > 10 else plt.cm.tab10.colors

        wedges, texts, autotexts = ax.pie(
            df_unique["Total_Songs"],
            labels=df_unique["Genre"],  
            autopct=lambda p: f'{p:.1f}%' if p > 0 else '',  
            startangle=140,
            colors=colors,  
            pctdistance=0.55,  
            labeldistance=1.2,  
            wedgeprops={'edgecolor': 'black'},
            textprops={'fontsize': 16, 'weight': 'bold'},  
            rotatelabels=True  
        )

        for text, wedge in zip(texts, wedges):
            x, y = text.get_position()  
            line_x, line_y = [x * 0.85, x], [y * 0.85, y]  
            ax.plot(line_x, line_y, color='black', linewidth=1.5)  

        plt.title(f"Distribution of Songs by Genre in {year}", fontsize=24, fontweight='bold', y=1.05)
        plt.axis("equal")  
        plt.show()

    def analyze_genre_statistics(self, year):
        if not self.validate_year(year):
            print(f"⚠ No data found for {year}. Please try another year.")
            return

        df = self.fetch_genre_statistics(year)

        if df.empty:
            print(f"⚠ No unique genre data available for {year}.")
            return

        self.format_output(df, year)

        # Add spacing between the table and the pie chart
        display(widgets.HTML("<br><br><br>"))  

        self.visualize_data(df, year)

# **Run Analysis for a Specific Year**
if __name__ == "__main__":
    database_path = "CWDatabase.db"
    analyzer = GenreStatisticsAnalyzer(database_path)

    try:
        year = int(input("Enter a year: "))
        analyzer.analyze_genre_statistics(year)
    except ValueError:
        print("⚠ Please enter a valid numeric year.")
