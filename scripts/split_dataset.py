import os
import pandas as pd

# define functions
def remove_duplicates(x):
  """
  Remove duplicates from dataframe x

  This function will remove duplicate values from 
  the original dataframe

  Return a set
  """
  set_of_x = set()
  # loop through all values and convert them to list
  for values in x:
    names = values.split(", ")
    # add values to set_of_transportation set
    for name in names:
      set_of_x.add(name)
  
  return set_of_x


def categorize_transportations(transportations):
  """
  Categorize transportations values by their keyword.

  Value with string Bandara will be categorized as airport,
  Value with string Terminal will be categorized as bus_station,
  Value with string Stasiun will be categorized as train_station.

  Return dataframes of categorized transportation
  """
  airport, bus_station, train_station = [], [], []
  
  # loop through set_of_transportation and 
  # add value to corresponding variable
  # according to their keyword
  set_of_transportations = remove_duplicates(transportations)
  for x in set_of_transportations:
    keyword = x.split()[0]
    if keyword == "Bandara":
      airport.append(x)
    elif keyword == "Terminal":
      bus_station.append(x)
    elif keyword == "Stasiun":
      train_station.append(x)

  return pd.DataFrame(data=airport, columns=["airport"]), pd.DataFrame(data=bus_station, columns=["bus_station"]), pd.DataFrame(data=train_station, columns=["train_station"])

    
# read raw dataset
dir_path = os.getcwd()
raw_dataset = pd.read_excel(dir_path + "/datasets/raw_dataset.xlsx")

# separate dataset by knowledge graph entities
cities = raw_dataset.filter(["city"], axis=1).drop_duplicates(inplace=False)
museums = raw_dataset.filter([
  "name", 
  "address", 
  "phone_number", 
  "email", "website", 
  "facebook", 
  "twitter", 
  "instagram", 
  "longitude", 
  "latitude"], axis=1)
  
transportations = raw_dataset.filter(["place_to_museum"], axis=1)
airport, bus_station, train_station = categorize_transportations(transportations["place_to_museum"])

entry_tickets = raw_dataset.filter(["entry_ticket_category"], axis=1)
other_tickets = raw_dataset.filter(["other_ticket_category"], axis=1)

print()
