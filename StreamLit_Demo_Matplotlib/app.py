import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import random

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

chart_type = st.sidebar.radio("Select Genre Chart Type", options=["Horizontal Bar Chart", "Pie Chart"])

fig, ax = plt.subplots(figsize=(10, 6))

if chart_type == "Horizontal Bar Chart":
    bars = ax.barh(genre_counts['Genre'], genre_counts['Count'], color=[genre_colors[genre] for genre in genre_counts['Genre']])
    ax.set_xlabel('Count')
    ax.set_ylabel('Genre')
    ax.set_title('Movie Genre Counts')
    ax.legend(bars, genre_counts['Genre'])
    plt.tight_layout()

    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            st.write('')
        with col2:
            st.pyplot(fig)

else:
    wedges, texts, autotexts = ax.pie(genre_counts['Count'], labels=genre_counts['Genre'], colors=[genre_colors[genre] for genre in genre_counts['Genre']], autopct='%1.1f%%')
    ax.set_title('Movie Genre Distribution')
    ax.legend(wedges, genre_counts['Genre'], loc='center left', bbox_to_anchor=(1, 0.5), title='Genre')
    plt.subplots_adjust(left=0.0, bottom=0.1, right=0.55)

    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            st.write('')
        with col2:
            st.pyplot(fig)

st.markdown('## Movie Title Comparison')

search_query = st.sidebar.text_input('Search Movie Titles')
search_query_lower = search_query.lower()
# Use the indexed column for faster search
search_results = df[df['title_lower'].str.contains(search_query_lower, case=False)]

title_chart_type = st.sidebar.radio("Select Title Chart Type", options=["Horizontal Bar Chart", "Pie Chart"])

fig, ax = plt.subplots(figsize=(10, 6))

if not search_results.empty and title_chart_type == "Horizontal Bar Chart":
    bars = ax.barh(search_results['title'], search_results['popularity'], color='dodgerblue')
    ax.set_xlabel('Popularity')
    ax.set_ylabel('Movie Title')
    ax.set_title('Movie Title Popularity Comparison')
    plt.tight_layout()

    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            st.write('')
        with col2:
            st.pyplot(fig)

elif not search_results.empty and title_chart_type == "Pie Chart":
    wedges, texts, autotexts = ax.pie(search_results['popularity'], labels=search_results['title'], autopct='%1.1f%%')
    ax.set_title('Movie Title Popularity Distribution')
    plt.subplots_adjust(left=0.0, bottom=0.1, right=0.55)

    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            st.write('')
        with col2:
            st.pyplot(fig)

elif search_results.empty:
    st.markdown('No matching movie titles found.')

st.markdown('## Top 5 Movies')

top_5_movies = df.nlargest(5, 'popularity')[['title', 'popularity']]
st.table(top_5_movies)
