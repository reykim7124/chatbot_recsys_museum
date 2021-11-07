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
museum = raw_dataset.filter([
    "name",
    "phone_number",
    "email", 
    "website",
    "facebook",
    "twitter",
    "instagram"], axis=1)

ticket_category = pd.DataFrame(data={"ticket_category": ["ticket 1", "ticket 2"]})
schedule_category = pd.DataFrame(data={"schedule_category": ["schedule 1", "schedule 2", "schedule 3"]})

tickets_1 = raw_dataset.filter(["ticket_1"], axis=1).rename(columns={"ticket_1":"ticket_type"})
tickets_2 = raw_dataset.filter(["ticket_2"], axis=1).dropna().rename(columns={"ticket_2":"ticket_type"})
ticket_type = tickets_1.append(tickets_2)

# remove duplicate data from entities
city = raw_dataset["city"].drop_duplicates(inplace=False).copy()
category = raw_dataset["category"].drop_duplicates(inplace=False).copy()
address = raw_dataset["address"].drop_duplicates(inplace=False).copy()
coordinate = raw_dataset[["latitude", "longitude"]].drop_duplicates(inplace=False).copy()

schedule_day = list(remove_duplicates(raw_dataset["schedule_1"].dropna()))
schedule_day = pd.DataFrame(data=schedule_day, columns=["schedule"])

ticket_type = list(remove_duplicates(ticket_type["ticket_type"]))
ticket_type = pd.DataFrame(data=ticket_type, columns=["ticket_type"])

transportation = list(remove_duplicates(raw_dataset["public_transportation"]))
transportation = pd.DataFrame(data=transportation, columns=["transportation"])

# create dataframe for knowledge graph city relation
museum_city = raw_dataset.filter(["name", "city"], axis=1)

# create dataframe for knowledge graph museum category relation
museum_category = raw_dataset.filter(["name", "category"], axis=1)

# create dataframe for knowledge graph transportation relation
museum_transportation = raw_dataset.filter(
    ["name", "public_transportation", "distance_to_museum"], axis=1)
museum_transportation = explode_datasets(museum_transportation, ["name"], [
    "public_transportation", "distance_to_museum"])

# create dataframe for knowledge graph addresses relation
museum_address = raw_dataset.filter(["name", "address"], axis=1)

# create dataframe for knowledge graph coordinates relation
museum_coordinate = raw_dataset.filter(["name", "city"], axis=1)

# create dataframe for knowledge graph ticket relation
museum_ticket_1 = raw_dataset.filter(["name", "ticket_1", "ticket_price_1"], axis=1)
museum_ticket_1 = explode_datasets(museum_ticket_1, ["name"], ["ticket_1", "ticket_price_1"])
museum_ticket_2 = raw_dataset.filter(["name", "ticket_2", "ticket_price_2", "ticket_name_2"], axis=1)
museum_ticket_2 = explode_datasets(museum_ticket_2, ["name", "ticket_name_2"], ["ticket_2", "ticket_price_2"])

# create dataframe for knowledge graph schedule relation
museum_schedule_1 = raw_dataset.filter(["name", "schedule_1", "schedule_name_1", "open_1", "closed_1"], axis=1)
museum_schedule_1 = explode_datasets(museum_schedule_1, ["name", "schedule_name_1", "open_1", "closed_1"], ["schedule_1"])
museum_schedule_2 = raw_dataset.filter(["name", "schedule_2", "schedule_name_2", "open_2", "closed_2"], axis=1)
museum_schedule_2 = explode_datasets(museum_schedule_2, ["name", "schedule_name_2", "open_2", "closed_2"], ["schedule_2"])
museum_schedule_3 = raw_dataset.filter(["name", "schedule_3", "schedule_name_3", "open_3", "closed_3"], axis=1)
museum_schedule_3 = explode_datasets(museum_schedule_3, ["name", "schedule_name_3", "open_3", "closed_3"], ["schedule_3"])

# write all entities and relations to csv
museum.to_csv(dir_path + "/datasets/split_dataset/museum.csv", index=False)
city.to_csv(dir_path + "/datasets/split_dataset//city.csv", index=False)
address.to_csv(dir_path + "/datasets/split_dataset/address.csv", index=False)
coordinate.to_csv(dir_path + "/datasets/split_dataset/coordinate.csv", index=False)
category.to_csv(dir_path + "/datasets/split_dataset/category.csv", index=False)
transportation.to_csv(dir_path + "/datasets/split_dataset/transportation.csv", index=False)
ticket_category.to_csv(dir_path + "/datasets/split_dataset/ticket_category.csv", index=False)
ticket_type.to_csv(dir_path + "/datasets/split_dataset/ticket_type.csv", index=False)
schedule_category.to_csv(dir_path + "/datasets/split_dataset/schedule_category.csv", index=False)
schedule_day.to_csv(dir_path + "/datasets/split_dataset/schedule_day.csv", index=False)
museum_city.to_csv(dir_path + "/datasets/split_dataset/museum_location.csv", index=False)
museum_category.to_csv(dir_path + "/datasets/split_dataset/museum_category.csv", index=False)
museum_transportation.to_csv(dir_path + "/datasets/split_dataset/museum_transportation.csv", index=False)
museum_ticket_1.to_csv(
    dir_path + "/datasets/split_dataset/museum_ticket_1.csv", index=False)
museum_ticket_2.to_csv(
    dir_path + "/datasets/split_dataset/museum_ticket_2.csv", index=False)
museum_schedule_1.to_csv(
    dir_path + "/datasets/split_dataset/museum_schedule_1.csv", index=False)
museum_schedule_2.to_csv(
    dir_path + "/datasets/split_dataset/museum_schedule_2.csv", index=False)
museum_schedule_3.to_csv(
    dir_path + "/datasets/split_dataset/museum_schedule_3.csv", index=False)
