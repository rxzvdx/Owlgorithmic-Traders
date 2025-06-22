# Author(s): 
#    Antonio Rosado
#    Kashan Khan
#    Imad Khan
#    Alexander Schifferle
#    Mike Kheang
# Assignment: 
#    Senior Project (Summer 2025) - "data_analyzer"
# Last Update: 
#    June 21st 2025
# Purpose: 
#    Formulate analytical insights using the extracted data from "pdf_parser"
from pdf_parser import *
import pandas as pd
import matplotlib
import os

# Creates a df from trade data
def create_df(path):
    # Load data from pdf
    trades = extract_trade_data_from_pdf(path)
    
    i = 0 # Dataframe Iterator
    
    # Iterates through 'trades' with interator 'trade'
    for trade in trades:
        temp_list = [] # Reset temp_list every loop
        
        # k is the key, v is the value
        for k,v in trade.items():
            temp_list.append(v) # value is stored in the list, temp_list
        # Store data in dictionary format for dataframe    
        listings = {f'row[i+1]': temp_list}
        if i == 0: # Create a new dataframe on first entry
            df = pd.DataFrame.from_dict(listings, orient='index',
                                        columns=['representative name', 'state district',
                                                 'owner', 'asset', 'transaction type',
                                                 'transaction date', 'notification date',
                                                'amount'])
        else:
            df.loc[i] = temp_list # Populate dataframe after first entry
        i += 1 # Iterate for dataframe
    return df

# Search through dataframe listings and records each asset instance without duplicates
def find_assets(df):
    # Sets list of asset name called asset_list
    asset_list = []

    # Reads dataframe, adds asset to list if not found in asset_list
    for index, row in df.iterrows():
        if row['asset'] not in asset_list:
            asset_list.append(row['asset'])
    return asset_list

# Creates a list of ratios from asset_list and df
def find_ratios(asset_list, df):
    # Create a dictionary to hold asset and their occurance in dataframe
    total_found_matches = {}
    for find_asset in asset_list:
        total_found_matches.update({find_asset: df['asset'].value_counts().get(find_asset, 0)})

    # Find percentage (float) of each asset found in dataframe
    ratio = 0
    ratio_dict = {}
    for item in total_found_matches:
        ratio = total_found_matches[item]/len(df)
        ratio_dict.update({item: ratio})

    # Create list to feed into plot.pie from pandas
    ratio_list = []
    for item in ratio_dict:
        ratio_list.append(ratio_dict[item])

    return ratio_list
    #Create a pie chart using values from find_assets() and find_ratios(asset_list) functions

def create_ratio_pie():
    asset_list = find_assets()
    ratio_list = find_ratios(asset_list)
    ratio_df = pd.DataFrame({'mass': ratio_list},
                             index=asset_list)
    return ratio_df.plot.pie(y='mass', figsize=(5,5))
