import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import random

st.set_page_config(layout="wide")

st.title('Top 10,000 Popular Movies')

# Cache function output to improve performance
with st.expander("Raw Dataset [Movie data](https://www.kaggle.com/datasets/ursmaheshj/top-10000-popular-movies-tmdb-05-2023?resource=download)"):
    @st.cache_data
    def load_data():
        df = pd.read_csv('popular_10000_movies_tmdb.csv')
        return df

    df = load_data()
    st.write(df)

st.markdown('## Data Visualization')

# Split genres column and keep only the first genre
df['Genre'] = df['genres'].str.split(',').str[0]

# Remove special characters from genre names
df['Genre'] = df['Genre'].apply(lambda x: re.sub(r"[\'\[\]]", "", x))

# Get unique genres
unique_genres = ['All Genres'] + df['Genre'].unique().tolist()

# Select genre(s) to display
genre_filter = st.sidebar.multiselect('Select Genre', unique_genres)

# Filter movies by genre
if 'All Genres' in genre_filter:
    filtered_df = df
else:
    filtered_df = df[df['Genre'].isin(genre_filter)]

# Filter movies by rating
rating_filter = st.sidebar.slider('Select Rating', min_value=float(df['vote_average'].min()), max_value=float(df['vote_average'].max()),
                                  value=(float(df['vote_average'].min()), float(df['vote_average'].max())))
filtered_df = filtered_df[(filtered_df['vote_average'] >= rating_filter[0]) & (filtered_df['vote_average'] <= rating_filter[1])]

# Count occurrences of each genre in the filtered dataset
genre_counts = filtered_df['Genre'].value_counts().reset_index()
genre_counts.columns = ['Genre', 'Count']
genre_counts = genre_counts.sort_values('Count', ascending=False)

# Assign random colors to each genre
genre_colors = {genre: f"#{random.randint(0, 0xFFFFFF):06x}" for genre in genre_counts['Genre'].unique()}

# Create an interactive chart based on user selection
chart_type = st.sidebar.radio("Select Chart Type", options=["Horizontal Bar Chart", "Pie Chart"])

if chart_type == "Horizontal Bar Chart":
    # Create a horizontal bar chart using Matplotlib
    plt.figure(figsize=(10, 6))
    bars = plt.barh(genre_counts['Genre'], genre_counts['Count'], color=[genre_colors[genre] for genre in genre_counts['Genre']])
    plt.xlabel('Count')
    plt.ylabel('Genre')
    plt.title('Movie Genre Counts')

    # Add legend
    plt.legend(bars, genre_counts['Genre'])
    plt.tight_layout()
    st.pyplot(plt)

else:
    # Create a pie chart using Matplotlib
    plt.figure(figsize=(6, 6))
    wedges, texts, autotexts = plt.pie(genre_counts['Count'], labels=genre_counts['Genre'], colors=[genre_colors[genre] for genre in genre_counts['Genre']], autopct='%1.1f%%')
    plt.title('Movie Genre Distribution')

    # Add legend without overlapping labels
    plt.legend(wedges, genre_counts['Genre'], loc='center left', bbox_to_anchor=(1, 0.5), title='Genre')

    # Adjust label positions to avoid overlap
    plt.subplots_adjust(left=0.0, bottom=0.1, right=0.55)

    st.pyplot(plt)

st.markdown('## Top 5 Movies')

# Select top 5 movies based on popularity
top_5_movies = df.nlargest(5, 'popularity')[['title', 'popularity']]
st.table(top_5_movies)
