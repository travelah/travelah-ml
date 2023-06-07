# -*- coding: utf-8 -*-
"""Copy of Travelah_Model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IaAR_7zt5ONhPihB_8h9mzY9sB2dcBEN
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords
import re
from nltk.corpus import stopwords as nltk_stopwords
import random

#Prepare dataset
travel_df = pd.read_csv("Data/travel_spot_datasets_final_updated_with_region.csv")
hotel_df = pd.read_csv('Data/booking_datasets_final_updated_with_region.csv')
food_df = pd.read_csv('Data/food_datasets_final_updated_with_region.csv')

#Text Cleaning
clean_spcl = re.compile('[/(){}\[\]\|@,;]')
clean_symbol = re.compile('[^0-9a-z #+_]')
stop_words = set(nltk_stopwords.words('english'))


def clean_df(text):
    if isinstance(text, list):
        text = ' '.join(text)
    text = text.lower()
    text = re.sub("[^a-zA-Z0-9 ]", "", str(text))
    text = clean_spcl.sub(' ', text)
    text = clean_symbol.sub('', text)
    text = ' '.join(word for word in text.split() if word not in stop_words)
    return text

# Drop Irrelevant Information
travel_df = travel_df.drop(["source"],axis=1)
travel_df = travel_df.drop_duplicates(subset='place')
food_df = food_df.drop(["source"],axis=1)
food_df = food_df.drop(["range"],axis=1)
food_df = food_df.drop_duplicates(subset='place_name')
hotel_df = hotel_df.drop(["source_href"],axis=1)
hotel_df = hotel_df.drop_duplicates(subset='name_hotel')


#selecting the relevant features for recommendation
selected_features_travel = ['rating_label', 'review_label','type_category','keywords','formatted_address','region']
selected_features_food = ['rating', 'cuisine','eating_type','price','region','formatted_region','comment','second_comment' ]
selected_features_hotel = ['formatted_region', 'price_label','rating_type','description', 'formatted_address', 'region']

#Replace the null values in the selected features with null string
for feature in selected_features_travel:
  travel_df[feature]= travel_df[feature].fillna('')
  travel_df[feature] = travel_df[feature].apply(clean_df)

for feature in selected_features_food:
  food_df[feature]= food_df[feature].fillna('')
  food_df[feature] = food_df[feature].apply(clean_df)

for feature in selected_features_hotel:
  hotel_df[feature]= hotel_df[feature].fillna('')
  hotel_df[feature] = hotel_df[feature].apply(clean_df)


# Reset the index of the DataFrame
travel_df = travel_df.reset_index(drop=True)
hotel_df = hotel_df.reset_index(drop=True)
food_df = food_df.reset_index(drop=True)


#Combine all the relevant features into one clean column
travel_df['combined_text'] = travel_df['place'] + ' ' + travel_df['region'] + ' ' + travel_df['type_category'] + ' ' + travel_df['keywords'] + ' ' + travel_df['formatted_address'] 
food_df['food_clean'] = food_df['formatted_region'] + ' ' + food_df['cuisine'] + ' ' + food_df['rating'] + ' '  + food_df['eating_type'] + ' '+ food_df['price'] + ' '+food_df['region'] + ' '+ food_df['comment'] + ' ' + food_df['second_comment'] 
hotel_df['desc_clean'] = hotel_df['formatted_region'] + ' ' +  hotel_df['price_label'] + ' '+ hotel_df['rating_type'] + ' '  + hotel_df['description'] + ' ' + hotel_df['formatted_address'] + ' '+ hotel_df['region'] 


# Check for missing values in 'combined_text' column
missing_indices_travel = travel_df['combined_text'].isnull()
if missing_indices_travel.any():
    travel_df.loc[missing_indices_travel, 'combined_text'] = ''

# Check for missing values in 'combined_text' column
missing_indices_food = food_df['food_clean'].isnull()
if missing_indices_food.any():
    food_df.loc[missing_indices_food, 'food_clean'] = ''

# Check for missing values in 'combined_text' column
missing_indices_hotel = hotel_df['desc_clean'].isnull()
if missing_indices_hotel.any():
    food_df.loc[missing_indices_hotel, 'food_clean'] = ''

vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), stop_words='english')
tfidf = vectorizer.fit_transform(travel_df['combined_text'])
tfidf_hotel = vectorizer.transform(hotel_df['desc_clean'])
tfidf_food = vectorizer.transform(food_df['food_clean'])

def check_region_travel(region):
    valid_regions = set(travel_df['region'])
    entered_region = clean_df(region.lower())

    for valid_region in valid_regions:
        if entered_region in valid_region:
            return True

    return False



def get_top_recommendations(df, num_recommendations):
    return df.head(num_recommendations)

def generate_itinerary(regions, travel_preferences, hotel_preferences, food_preferences, duration):
    itinerary = "Great! Here's your itinerary for your trip:\n\n"

    num_days_per_region = duration // len(regions)
    remaining_days = duration % len(regions)

    for i, region in enumerate(regions):
        if i == len(regions) - 1:
            if remaining_days > 0:
                itinerary += f"Day {i*num_days_per_region+1}-{i*num_days_per_region+num_days_per_region+remaining_days}: {region}\n"
                remaining_days -= 1
            else:
                itinerary += f"Day {i*num_days_per_region+1}-{i*num_days_per_region+num_days_per_region}: {region}\n"
        else:
            itinerary += f"Day {i*num_days_per_region+1}-{i*num_days_per_region+num_days_per_region}: {region}\n"

        # Travel Spot Recommendations
        travel_results = pd.DataFrame()
        travel_results = search_travel_spot(region, travel_preferences)
        num_travel_recommendations = min(10, len(travel_results))
        top_travel_recommendations = get_top_recommendations(travel_results, num_travel_recommendations)
        travel_recommendations = top_travel_recommendations.head(5)
        
        if not travel_recommendations.empty:
            itinerary += f"Stay at the "
            
            # Hotel Recommendation
            hotel_results = pd.DataFrame()
            hotel_results = search_hotels(region, hotel_preferences)
            num_hotel_recommendations = min(10, len(hotel_results))
            top_hotel_recommendations = get_top_recommendations(hotel_results, num_hotel_recommendations)

            # Select hotel recommendation
            hotel_recommendation = top_hotel_recommendations.head(1)
            
            if not hotel_recommendation.empty:
                itinerary += f"{hotel_recommendation['name_hotel'].iloc[0]} or any other hotel of your choice from the list.\n"

                if not travel_recommendations.empty:
                    itinerary += "Explore "
                    for _, spot in travel_recommendations.iterrows():
                        itinerary += spot['place'] + ", "
                    itinerary = itinerary[:-2] + ".\n\n"
                else:
                    itinerary += "\n"

                # Food Place Recommendations
                food_results = pd.DataFrame()
                food_results = search_food(region, food_preferences)
                num_food_recommendations = min(10, len(food_results))
                top_food_recommendations = get_top_recommendations(food_results, num_food_recommendations)
                top_food_recommendations = food_results.head(5)

                if not top_food_recommendations.empty:
                    itinerary += "Recommendations for places to eat near you:\n"
                    for _, food in top_food_recommendations.iterrows():
                        itinerary += "- " + food['place_name'] + "\n"
                    itinerary += "\n"
                else:
                    itinerary += "No food recommendations found.\n\n"
            else:
                itinerary += "No hotel recommendations found.\n\n"
        else:
            itinerary += "No travel recommendations found.\n\n"

    return itinerary

def search_travel_spot(region, query):


    # Join the query list into a string
    query_string = ' '.join(query)

    # Split the query into individual parameters
    parameters = query_string.split(',')

    results = pd.DataFrame()

    for preference in parameters:
        # Prepare the query string with the current preference
        query_string = f"{region} {preference.strip()}"
        query_vector = vectorizer.transform([query_string])
        similarity_scores = cosine_similarity(query_vector, tfidf).flatten()

        # Filter based on region
        region_indices = travel_df['region'].str.contains(region, case=False, regex=False)
        filtered_scores = similarity_scores * region_indices

        top_indices = filtered_scores.argsort()[::-1]
        preference_results = travel_df.iloc[top_indices]

        results = pd.concat([results, preference_results], ignore_index=True)

    return results

def search_hotels(region, query):
    # Join the query list into a string
    query_string = ' '.join(query)

    # Split the query into individual parameters
    parameters = query_string.split(',')

    # Prepare the query string with all the parameters
    query_string = f"{region} {' '.join(parameters)}"
    query_vector = vectorizer.transform([query_string])
    similarity_scores = cosine_similarity(query_vector, tfidf_hotel).flatten()

    # Filter based on region
    region_indices = hotel_df['formatted_region'].str.contains(region, case=False, regex=False)
    filtered_scores = similarity_scores * region_indices

    top_indices = filtered_scores.argsort()[::-1]
    results = hotel_df.iloc[top_indices]
    return results

def search_food(region, query):
    # Join the query list into a string
    query_string = ' '.join(query)

    # Split the query into individual parameters
    parameters = query_string.split(',')

    results = pd.DataFrame()
    for preference in parameters:
        # Prepare the query string with the current preference
        query_string = f"{region} {preference.strip()}"
        query_vector = vectorizer.transform([query_string])
        similarity_scores = cosine_similarity(query_vector, tfidf_food).flatten()

        # Filter based on region
        region_indices = food_df['formatted_region'].str.contains(region, case=False, regex=False)
        filtered_scores = similarity_scores * region_indices

        top_indices = filtered_scores.argsort()[::-1]
        preference_results = food_df.iloc[top_indices]

        results = pd.concat([results, preference_results], ignore_index=True)

    return results

def check_region_travel(region):
    valid_regions = set(travel_df['region'])
    entered_region = clean_df(region.lower())

    for valid_region in valid_regions:
        if entered_region in valid_region:
            return True

    return False

def clean_df(text):
    # Apply any necessary cleaning to the text
    return text

def get_user_input(prompt):
    return input(prompt)

def display_output(output):
    print(output)

def main():
    region_input_travel = get_user_input("Enter the Regions for Travel (comma-separated): ")
    place_input_travel = get_user_input("Enter your Location/Type of Place for Travel: ")
    place_input_hotel = get_user_input("Enter your Description/Keywords for Hotel: ")
    food_input = get_user_input("Enter your Food Preferences: ")
    duration_input = get_user_input("Enter the Duration of Travel (in days): ")

    regions = [region.strip() for region in region_input_travel.split(',')]  # Strip whitespace around each region
    travel_preferences = place_input_travel.split(',')
    hotel_preferences = place_input_hotel.split(',')
    food_preferences = food_input.split(',')
    duration = duration_input

    if len(regions) > 0 and len(travel_preferences) > 0 and len(hotel_preferences) > 0 and len(food_preferences) > 0 and duration.isdigit() and int(duration) > 0:
        valid_regions = []
        for region in regions:
            if check_region_travel(region):
                valid_regions.append(region.strip())

        if valid_regions:
            itinerary = generate_itinerary(valid_regions, travel_preferences, hotel_preferences, food_preferences, int(duration))
            display_output(itinerary)
        else:
            display_output("Sorry, the entered regions are not valid.")
    else:
        display_output("Please enter valid regions, location/type of place for travel, description/keywords for hotel, food preferences, and duration of travel (in days).")

if __name__ == '__main__':
    main()
