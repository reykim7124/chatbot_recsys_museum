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
  airports, bus_stations, train_stations = [], [], []
  
  # loop through set_of_transportation and 
  # add value to corresponding variable
  # according to their keyword
  set_of_transportations = remove_duplicates(transportations)
  for x in set_of_transportations:
    keyword = x.split()[0]
    if keyword == "Bandara":
      airports.append(x)
    elif keyword == "Terminal":
      bus_stations.append(x)
    elif keyword == "Stasiun":
      train_stations.append(x)

  return pd.DataFrame(data=airports, columns=["airport"]), pd.DataFrame(data=bus_stations, columns=["bus_station"]), pd.DataFrame(data=train_stations, columns=["train_station"])

    
# read raw dataset
dir_path = os.getcwd()
raw_dataset = pd.read_excel(dir_path + "/datasets/raw_dataset.xlsx")

# create data frame for knowledge graph entities
cities = raw_dataset.filter(["city"], axis=1)
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
entry_ticket_category = raw_dataset.filter(["entry_ticket_category"], axis=1)
other_ticket_category = raw_dataset.filter(["other_ticket_category"], axis=1)

# categorize categorical dataframe
airports, bus_stations, train_stations = categorize_transportations(transportations["place_to_museum"])

# remove duplicate data from entities
city = cities.drop_duplicates(inplace=False).copy()

entry_tickets = list(remove_duplicates(entry_ticket_category["entry_ticket_category"]))
entry_tickets = pd.DataFrame(data=entry_tickets, columns=["entry_ticket"])

other_tickets = list(remove_duplicates(other_ticket_category["other_ticket_category"].dropna()))
other_tickets = pd.DataFrame(data=other_tickets, columns=["other_ticket"])

# create dataframe for knowledge graph location relation
museums_location = museums.copy()
museums_location["city"] = cities.values

# create dataframe for knowledge graph transportation relation
museum_transportations = museums.copy()
museum_transportations["place_to_museum"] = transportations.values
museum_transportations["distance_to_museum"] = raw_dataset["distance_to_museum"].values

# create dataframe for knowledge graph entry ticket category relation 
museums_entry_ticket = museums.copy()
museums_entry_ticket["entry_ticket_category"] = entry_ticket_category.values
museums_entry_ticket["entry_ticket_price"] = raw_dataset["entry_ticket_price"].values

# create dataframe for knowledge graph other ticket category relation
museums_other_ticket = museums.copy()
museums_other_ticket["other_ticket_category"] = other_ticket_category.values
museums_other_ticket["other_ticket_price"] = raw_dataset["other_ticket_price"].values
museums_other_ticket["other_ticket_name"] = raw_dataset["other_ticket_name"].values
museums_other_ticket.dropna(inplace=True, subset=["other_ticket_name"])

# write all entities and relations to csv
museums.to_csv(dir_path + "/datasets/museum.csv", index=False)
city.to_csv(dir_path + "/datasets/city.csv", index=False)
airports.to_csv(dir_path + "/datasets/airport.csv", index=False)
bus_stations.to_csv(dir_path + "/datasets/bus_station.csv", index=False)
train_stations.to_csv(dir_path + "/datasets/train_station.csv", index=False)
entry_tickets.to_csv(dir_path + "/datasets/entry_ticket.csv", index=False)
other_tickets.to_csv(dir_path + "/datasets/other_ticket.csv", index=False)
museums_location.to_csv(dir_path + "/datasets/museum_location.csv", index=False)
museum_transportations.to_csv(dir_path + "/datasets/museum_transportation.csv", index=False)
museums_entry_ticket.to_csv(dir_path + "/datasets/museum_entry_ticket.csv", index=False)
museums_other_ticket.to_csv(dir_path + "/datasets/museum_other_ticket.csv", index=False)
