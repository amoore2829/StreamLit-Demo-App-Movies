import streamlit as st
import pandas as pd
import traceback
import re

@st.cache(allow_output_mutation=True)
def load_data():
    try:
        df = pd.read_csv('popular_10000_movies_tmdb.csv')
        return df
    except FileNotFoundError:
        st.error("Dataset file not found.")
    except Exception as e:
        st.error(f"An error occurred while loading the dataset: {str(e)}")
        st.error(traceback.format_exc())
    return None

@st.cache(allow_output_mutation=True)
def preprocess_data(df):
    try:
        df['Genre'] = df['genres'].str.split(',').str[0]
        df['Genre'] = df['Genre'].apply(lambda x: re.sub(r"[\'\[\]]", "", x))
        df['title_lower'] = df['title'].str.lower()
        return df
    except Exception as e:
        st.error(f"An error occurred while preprocessing the data: {str(e)}")
        st.error(traceback.format_exc())
    return None
