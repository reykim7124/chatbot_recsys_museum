from typedb.client import TypeDB, SessionType, TransactionType
import os
import csv


def build_museum_recsys_chatbot_graph(inputs):
    with TypeDB.core_client("localhost:1729") as client:
        with client.session("museum_recsys_chatbot", SessionType.DATA) as session:
            for input in inputs:
                print(
                    "Loading from [" + input["data_path"] + "] into TypeDB ...")
                load_data_into_typedb(input, session)


def parse_data_to_dictionaries(input):
    items = []
    with open(input["data_path"] + ".csv") as data:
        for row in csv.DictReader(data, skipinitialspace=True):
            item = {key: value for key, value in row.items()}
            items.append(item)
    return items


def load_data_into_typedb(input, session):
    items = parse_data_to_dictionaries(input)

    for item in items:
        with session.transaction(TransactionType.WRITE) as transaction:
            typeql_insert_query = input["template"](item)
            print("Executing TypeQL Query: " + typeql_insert_query)
            transaction.query().insert(typeql_insert_query)
            transaction.commit()

    print("\nInserted " + str(len(items)) +
          " items from [ " + input["data_path"] + "] into TypeDB.\n")


def museum_template(museum):
    typeql_insert_query = "insert $museum isa museum"
    typeql_insert_query += ', has name "' + museum["name"] + '"'
    typeql_insert_query += ', has address "' + museum["address"] + '"'
    typeql_insert_query += ', has phone-number "' + \
        museum["phone_number"] + '"'
    typeql_insert_query += ', has longitude ' + museum["longitude"] + ''
    typeql_insert_query += ', has latitude ' + museum["latitude"] + ''

    if "email" in museum:
        typeql_insert_query += ', has email "' + museum["email"] + '"'

    if "website" in museum:
        typeql_insert_query += ', has website "' + museum["website"] + '"'

    if "facebook" in museum:
        typeql_insert_query += ', has facebook "' + museum["facebook"] + '"'

    if "twitter" in museum:
        typeql_insert_query += ', has twitter "' + museum["twitter"] + '"'

    if "instagram" in museum:
        typeql_insert_query += ', has instagram "' + museum["instagram"] + '";'

    return typeql_insert_query


def city_template(city):
    return 'insert $city isa city, has name "' + city["city"] + '";'


def category_template(category):
    return 'insert $category isa category, has name "' + category["category"] + '";'


def airport_template(airport):
    return 'insert $airport isa airport, has name "' + airport["airport"] + '";'


def bus_station_template(bus_station):
    return 'insert $bus-station isa bus-station, has name "' + bus_station["bus_station"] + '";'


def train_station_template(train_station):
    return 'insert $train-station isa train-station, has name "' + train_station["train_station"] + '";'


def ticket_template(ticket):
    return 'insert $ticket isa ticket, has name "' + ticket["ticket"] + '";'


def schedule_template(schedule):
    return 'insert $schedule isa schedule, has name "' + schedule["schedule"] + '";'


def museum_location_template(museum_location):
    typeql_insert_query = 'match $museum isa museum, has name "' + \
        museum_location["name"] + '";'
    typeql_insert_query += ' $city isa city, has name "' + \
        museum_location["city"] + '";'
    typeql_insert_query += ' insert (location-for: $museum, located-in: $city) isa location;'
    return typeql_insert_query


def museum_category_template(museum_category):
    typeql_insert_query = 'match $museum isa museum, has name "' + \
        museum_category["name"] + '";'
    typeql_insert_query += ' $category isa category, has name "' + \
        museum_category["category"] + '";'
    typeql_insert_query += ' insert (category-for: $museum, categorize-as: $category) isa museum-category;'
    return typeql_insert_query


def museum_transportation_template(museum_transportation):
    typeql_insert_query = 'match $museum isa museum, has name "' + \
        museum_transportation["name"] + '";'
    transport = museum_transportation["public_transportation"]
    keyword = transport.split()[0]
    if keyword == "Bandara":
        typeql_insert_query += ' $transportation isa airport, has name "' + transport + '";'
    elif keyword == "Terminal":
        typeql_insert_query += ' $transportation isa bus-station, has name "' + transport + '";'
    elif keyword == "Stasiun":
        typeql_insert_query += ' $transportation isa train-station, has name "' + transport + '";'

    typeql_insert_query += ' insert (destination-to: $museum, destination-from: $transportation) isa transport'
    typeql_insert_query += ', has distance ' + \
        museum_transportation["distance_to_museum"] + ';'

    return typeql_insert_query


def museum_ticket_1_template(museum_ticket_1):
    typeql_insert_query = 'match $museum isa museum, has name "' + \
        museum_ticket_1["name"] + '";'
    typeql_insert_query += ' $ticket isa ticket, has name "' + \
        museum_ticket_1["ticket_1"] + '";'
    typeql_insert_query += ' insert (ticket-1-for: $museum, entry-1-for: $ticket) isa ticket-1'
    typeql_insert_query += ', has price ' + \
        museum_ticket_1['ticket_price_1'] + ';'
    return typeql_insert_query


def museum_ticket_2_template(museum_ticket_2):
    typeql_insert_query = 'match $museum isa museum, has name "' + \
        museum_ticket_2["name"] + '";'
    typeql_insert_query += ' $ticket isa ticket, has name "' + \
        museum_ticket_2["ticket_2"] + '";'
    typeql_insert_query += ' insert (ticket-2-for: $museum, entry-2-for: $ticket) isa ticket-2'
    typeql_insert_query += ', has name "' + \
        museum_ticket_2["ticket_name_2"] + '"'
    typeql_insert_query += ', has price ' + \
        museum_ticket_2['ticket_price_2'] + ';'
    return typeql_insert_query


def museum_schedule_1_template(museum_schedule_1):
    typeql_insert_query = 'match $museum isa museum, has name "' + \
        museum_schedule_1["name"] + '";'
    typeql_insert_query += ' $schedule isa schedule, has name "' + \
        museum_schedule_1["schedule_1"] + '";'
    typeql_insert_query += ' insert (schedule-1-for: $museum, schedule-1-at: $schedule) isa schedule-1'

    if "schedule_name_1" in museum_schedule_1:
        typeql_insert_query += ', has name "' + \
            museum_schedule_1["schedule_name_1"] + '"'

    typeql_insert_query += ', has open "' + museum_schedule_1["open_1"] + '"'
    typeql_insert_query += ', has closed "' + \
        museum_schedule_1["closed_1"] + '";'
    return typeql_insert_query


def museum_schedule_2_template(museum_schedule_2):
    typeql_insert_query = 'match $museum isa museum, has name "' + \
        museum_schedule_2["name"] + '";'
    typeql_insert_query += ' $schedule isa schedule, has name "' + \
        museum_schedule_2["schedule_2"] + '";'
    typeql_insert_query += ' insert (schedule-2-for: $museum, schedule-2-at: $schedule) isa schedule-2'

    if "schedule_name_2" in museum_schedule_2:
        typeql_insert_query += ', has name "' + \
            museum_schedule_2["schedule_name_2"] + '"'

    typeql_insert_query += ', has open "' + museum_schedule_2["open_2"] + '"'
    typeql_insert_query += ', has closed "' + \
        museum_schedule_2["closed_2"] + '";'
    return typeql_insert_query


def museum_schedule_3_template(museum_schedule_3):
    typeql_insert_query = 'match $museum isa museum, has name "' + \
        museum_schedule_3["name"] + '";'
    typeql_insert_query += ' $schedule isa schedule, has name "' + \
        museum_schedule_3["schedule_3"] + '";'
    typeql_insert_query += ' insert (schedule-3-for: $museum, schedule-3-at: $schedule) isa schedule-3'

    if "schedule_name_3" in museum_schedule_3:
        typeql_insert_query += ', has name "' + \
            museum_schedule_3["schedule_name_3"] + '"'

    typeql_insert_query += ', has open "' + museum_schedule_3["open_3"] + '"'
    typeql_insert_query += ', has closed "' + \
        museum_schedule_3["closed_3"] + '";'
    return typeql_insert_query


dir_path = os.getcwd()
# file path & functions for inserting data to knowledge graph
inputs = [
    {
        "data_path": dir_path + "/datasets/museum",
        "template": museum_template
    },
    {
        "data_path": dir_path + "/datasets/city",
        "template": city_template
    },
    {
        "data_path": dir_path + "/datasets/category",
        "template": category_template
    },
    {
        "data_path": dir_path + "/datasets/airport",
        "template": airport_template
    },
    {
        "data_path": dir_path + "/datasets/bus_station",
        "template": bus_station_template
    },
    {
        "data_path": dir_path + "/datasets/train_station",
        "template": train_station_template
    },
    {
        "data_path": dir_path + "/datasets/ticket",
        "template": ticket_template
    },
    {
        "data_path": dir_path + "/datasets/schedule",
        "template": schedule_template
    },
    {
        "data_path": dir_path + "/datasets/museum_location",
        "template": museum_location_template
    },
    {
        "data_path": dir_path + "/datasets/museum_category",
        "template": museum_category_template
    },
    {
        "data_path": dir_path + "/datasets/museum_transportation",
        "template": museum_transportation_template
    },
    {
        "data_path": dir_path + "/datasets/museum_ticket_1",
        "template": museum_ticket_1_template
    },
    {
        "data_path": dir_path + "/datasets/museum_ticket_2",
        "template": museum_ticket_2_template
    },
    {
        "data_path": dir_path + "/datasets/museum_schedule_1",
        "template": museum_schedule_1_template
    },
    {
        "data_path": dir_path + "/datasets/museum_schedule_2",
        "template": museum_schedule_2_template
    },
    {
        "data_path": dir_path + "/datasets/museum_schedule_3",
        "template": museum_schedule_3_template
    },
]

build_museum_recsys_chatbot_graph(inputs)
