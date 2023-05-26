import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import random
import requests

st.set_page_config(layout="wide")

@st.cache_data  # Cache function output to improve performance
def load_data():
    df = pd.read_csv('popular_10000_movies_tmdb.csv')
    return df

@st.cache_data  # Cache preprocessing steps
def preprocess_data(df):
    df['Genre'] = df['genres'].str.split(',').str[0]
    df['Genre'] = df['Genre'].apply(lambda x: re.sub(r"[\'\[\]]", "", x))
    # Create an index for faster search
    df['title_lower'] = df['title'].str.lower()
    return df

def get_movie_image_url(title):
    query = f"{title} movie poster"
    for j in search(query, num_results=1):
        if "imdb.com" in j:
            continue
        return j
    return ""

def get_movie_image(title):
    image_url = get_movie_image_url(title)
    if image_url:
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        return image
    return None

df = load_data()
df = preprocess_data(df)

st.title('Top 10,000 Popular Movies')

with st.expander("Raw Dataset [Download Here](https://www.kaggle.com/datasets/ursmaheshj/top-10000-popular-movies-tmdb-05-2023?resource=download)"):
    st.write(df)

st.markdown('## Data Visualization')

unique_genres = ['All Genres'] + df['Genre'].unique().tolist()

genre_filter = st.sidebar.multiselect('Select Genre', unique_genres)

if 'All Genres' in genre_filter:
    filtered_df = df
else:
    filtered_df = df[df['Genre'].isin(genre_filter)]

rating_filter = st.sidebar.slider('Select Rating', min_value=float(df['vote_average'].min()), max_value=float(df['vote_average'].max()),
                                  value=(float(df['vote_average'].min()), float(df['vote_average'].max())))
filtered_df = filtered_df[(filtered_df['vote_average'] >= rating_filter[0]) & (filtered_df['vote_average'] <= rating_filter[1])]

genre_counts = filtered_df['Genre'].value_counts().reset_index()
genre_counts.columns = ['Genre', 'Count']
genre_counts = genre_counts.sort_values('Count', ascending=False)

genre_colors = {genre: f"#{random.randint(0, 0xFFFFFF):06x}" for genre in genre_counts['Genre'].unique()}

# How to Use
with st.expander("How to Use"):
    st.markdown("""
    1. Use the **Genre** filter on the left sidebar to select specific movie genres or choose **All Genres** to include all genres.
    2. Adjust the **Rating** slider to filter movies based on their average ratings. Drag the slider handles to set the minimum and maximum rating values.
    3. The filtered dataset will be updated automatically, and the charts will reflect the selected filters.
    """)

# Display genre filter
st.sidebar.markdown('## Filter')
st.sidebar.markdown('### Genre')
chart_type_genre = st.sidebar.selectbox('Chart Type', ['Horizontal Bar Chart', 'Pie Chart'])
if chart_type_genre == 'Horizontal Bar Chart':
    fig, ax = plt.subplots()
    bars = ax.barh(genre_counts['Genre'], genre_counts['Count'], color=[genre_colors[genre] for genre in genre_counts['Genre']])
    ax.set_xlabel('Count')
    ax.set_ylabel('Genre')
    ax.set_title('Movie Genre Distribution')
    st.pyplot(fig)
else:
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(genre_counts['Count'], labels=genre_counts['Genre'], colors=[genre_colors[genre] for genre in genre_counts['Genre']], autopct='%1.1f%%')
    ax.set_title('Movie Genre Distribution')
    st.pyplot(fig)

search_query = st.sidebar.text_input('Search Movie Titles')
search_query_lower = search_query.lower()
search_results = df[df['title_lower'].str.contains(search_query_lower, case=False)]

# Horizontal bar chart for movie title popularity comparison
if not search_results.empty:
    fig, ax = plt.subplots()
    bars = ax.barh(search_results['title'], search_results['popularity'], color='dodgerblue')
    ax.set_xlabel('Popularity')
    ax.set_ylabel('Movie Title')
    ax.set_title('Movie Title Popularity Comparison')
    st.pyplot(fig)

top_5_movies = df.nlargest(5, 'popularity')[['title', 'popularity']]

# Horizontal bar chart for top 5 movies by popularity
fig, ax = plt.subplots()
bars = ax.barh(top_5_movies['title'], top_5_movies['popularity'], color='green')
ax.set_xlabel('Popularity')
ax.set_ylabel('Movie Title')
ax.set_title('Top 5 Movies by Popularity')
st.pyplot(fig)

# Select random movies from the dataset
random_movies = df.sample(100)

# Create a 2x2 grid
fig, axes = plt.subplots(2, 2, figsize=(10, 10))

# Pie chart of original_language
ax = axes[0, 0]
language_counts = random_movies['original_language'].value_counts()
ax.pie(language_counts, labels=language_counts.index, autopct='%1.1f%%')
ax.set_title('Original Language')

# Line chart of release_date
ax = axes[0, 1]
release_dates = pd.to_datetime(random_movies['release_date'])
ax.plot(release_dates, random_movies['popularity'], color='orange')
ax.set_xlabel('Release Date')
ax.set_ylabel('Popularity')
ax.set_title('Release Date vs Popularity')

# Scatter plot of budget vs popularity
ax = axes[1, 0]
ax.scatter(random_movies['budget'], random_movies['popularity'], alpha=0.5, color='green')
ax.set_xlabel('Budget')
ax.set_ylabel('Popularity')
ax.set_title('Budget vs Popularity')

# Dot plot of production_companies
ax = axes[1, 1]
company_counts = random_movies['production_companies'].str.split(',').apply(len)
ax.plot(company_counts, range(len(company_counts)), 'bo')
ax.set_xlabel('Number of Production Companies')
ax.set_ylabel('Movie Index')
ax.set_title('Number of Production Companies')

# Adjust spacing between subplots
plt.tight_layout()

# Display the 2x2 grid
st.pyplot(fig)
