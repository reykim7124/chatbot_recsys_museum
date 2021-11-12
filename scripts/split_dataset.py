import os
import pandas as pd


def remove_duplicates(x):
    """
    Remove duplicates from dataframe x

    This function will remove duplicate values from 
    the original dataframe

    Return a set
    """
    x = x.apply(lambda x: x.split(", "))
    x = x.explode()
    x = x.drop_duplicates()
    return set(x)


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


def explode_datasets(df, idx, col):
    """
    Split cell with string that contains multiple data
    By using the explode method provided by pandas
    """
    for x in col:
        if x:
            try:
                df[x] = df[x].apply(lambda x: x.split(", "))
            except AttributeError:
                df[x] = df[x].apply(lambda x: str(x).split(", "))

    return df.set_index(idx).apply(pd.Series.explode).reset_index()


# read raw dataset
dir_path = os.getcwd()
raw_dataset = pd.read_excel(dir_path + "/datasets/raw_dataset.xlsx")

# create data frame for knowledge graph entities
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

tickets_1 = raw_dataset.filter(["ticket_1"], axis=1).rename(columns={"ticket_1":"ticket"})
tickets_2 = raw_dataset.filter(["ticket_2"], axis=1).dropna().rename(columns={"ticket_2":"ticket"})
tickets = tickets_1.append(tickets_2)

# categorize categorical dataframe
airports, bus_stations, train_stations = categorize_transportations(
    raw_dataset["public_transportation"])

# remove duplicate data from entities
city = raw_dataset["city"].drop_duplicates(inplace=False).copy()
category = raw_dataset["category"].drop_duplicates(inplace=False).copy()

schedule = list(remove_duplicates(raw_dataset["schedule_1"].dropna()))
schedule = pd.DataFrame(data=schedule, columns=["schedule"])

ticket = list(remove_duplicates(tickets["ticket"]))
ticket = pd.DataFrame(data=ticket, columns=["ticket"])

# create dataframe for knowledge graph location relation
museum_location = raw_dataset.filter(["name", "city"], axis=1)

# create dataframe for knowledge graph museum category relation
museum_category = raw_dataset.filter(["name", "category"], axis=1)

# create dataframe for knowledge graph transportation relation
museum_transportation = raw_dataset.filter(
    ["name", "public_transportation", "distance_to_museum"], axis=1)
museum_transportation = explode_datasets(museum_transportation, ["name"], [
    "public_transportation", "distance_to_museum"])

# create dataframe for knowledge graph ticket category relation
museum_ticket_1 = raw_dataset.filter(
    ["name", "ticket_1", "ticket_price_1"], axis=1)
museum_ticket_1 = explode_datasets(museum_ticket_1, ["name"], [
    "ticket_1", "ticket_price_1"])

museum_ticket_2 = raw_dataset.filter(
    ["name", "ticket_name_2", "ticket_2", "ticket_price_2"], axis=1)
museum_ticket_2.dropna(inplace=True, subset=["ticket_name_2"])
museum_ticket_2 = explode_datasets(
    museum_ticket_2, ["name", "ticket_name_2"], ["ticket_2", "ticket_price_2"])

# create dataframe for knowledge graph schedule category relation
museum_schedule_1 = raw_dataset.filter(
    ["name", "schedule_1", "schedule_name_1", "open_1", "closed_1"], axis=1)
museum_schedule_1 = explode_datasets(museum_schedule_1, [
                                     "name", "schedule_name_1", "open_1", "closed_1"], ["schedule_1"])

museum_schedule_2 = raw_dataset.filter(
    ["name", "schedule_2", "schedule_name_2", "open_2", "closed_2"], axis=1)
museum_schedule_2.dropna(inplace=True, subset=["schedule_2"])
museum_schedule_2 = explode_datasets(museum_schedule_2, [
                                     "name", "schedule_name_2", "open_2", "closed_2"], ["schedule_2"])

museum_schedule_3 = raw_dataset.filter(
    ["name", "schedule_3", "schedule_name_3", "open_3", "closed_3"], axis=1)
museum_schedule_3.dropna(inplace=True, subset=["schedule_3"])
museum_schedule_3 = explode_datasets(museum_schedule_3, [
                                     "name", "schedule_name_3", "open_3", "closed_3"], ["schedule_3"])

# write all entities and relations to csv
museums.to_csv(dir_path + "/datasets/museum.csv", index=False)
city.to_csv(dir_path + "/datasets/city.csv", index=False)
category.to_csv(dir_path + "/datasets/category.csv", index=False)
airports.to_csv(dir_path + "/datasets/airport.csv", index=False)
bus_stations.to_csv(dir_path + "/datasets/bus_station.csv", index=False)
train_stations.to_csv(dir_path + "/datasets/train_station.csv", index=False)
ticket.to_csv(dir_path + "/datasets/ticket.csv", index=False)
schedule.to_csv(dir_path + "/datasets/schedule.csv", index=False)
museum_location.to_csv(
    dir_path + "/datasets/museum_location.csv", index=False)
museum_category.to_csv(
    dir_path + "/datasets/museum_category.csv", index=False)
museum_transportation.to_csv(
    dir_path + "/datasets/museum_transportation.csv", index=False)
museum_ticket_1.to_csv(
    dir_path + "/datasets/museum_ticket_1.csv", index=False)
museum_ticket_2.to_csv(
    dir_path + "/datasets/museum_ticket_2.csv", index=False)
museum_schedule_1.to_csv(
    dir_path + "/datasets/museum_schedule_1.csv", index=False)
museum_schedule_2.to_csv(
    dir_path + "/datasets/museum_schedule_2.csv", index=False)
museum_schedule_3.to_csv(
    dir_path + "/datasets/museum_schedule_3.csv", index=False)
