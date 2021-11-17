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
    typeql_insert_query += ', has place-name "' + museum["name"] + '"'
    typeql_insert_query += ', has phone-number "' + \
        museum["phone_number"] + '"'

    if "email" in museum:
        typeql_insert_query += ', has email "' + museum["email"] + '"'

    if "website" in museum:
        typeql_insert_query += ', has website "' + museum["website"] + '"'

    if "facebook" in museum:
        typeql_insert_query += ', has facebook "' + museum["facebook"] + '"'

    if "twitter" in museum:
        typeql_insert_query += ', has twitter "' + museum["twitter"] + '"'

    if "instagram" in museum:
        typeql_insert_query += ', has instagram "' + museum["instagram"] + '"'

    typeql_insert_query += ';'

    return typeql_insert_query


def city_template(city):
    return 'insert $city isa city, has place-name "' + city["city"] + '";'


def category_template(category):
    return 'insert $category isa museum-category, has category-name "' + category["category"] + '";'


def address_template(address):
    return 'insert $address isa address, has address-text "' + address["address"] + '";'


def transportation_template(transportation):
    return 'insert $transportation isa transportation, has place-name "' + transportation["transportation"] + '";'


def transportation_type_template(transportation_type):
    return 'insert $tty isa transportation-type, has category-name "' + transportation_type["transportation_type"] + '";'


def coordinate_template(coordinate):
    typeql_insert_query = 'insert $coordinate isa coordinate'
    typeql_insert_query += ', has latitude ' + coordinate["latitude"] + ''
    typeql_insert_query += ', has longitude ' + coordinate["longitude"] + ';'
    return typeql_insert_query


def ticket_category_template(ticket):
    return 'insert $ticket isa ticket-category, has category-name "' + ticket["ticket_category"] + '";'


def ticket_type_template(ticket):
    return 'insert $ticket isa ticket-type, has ticket-name "' + ticket["ticket_type"] + '";'


def schedule_category_template(schedule):
    return 'insert $schedule isa schedule-category, has category-name "' + schedule["schedule_category"] + '";'


def schedule_day_template(schedule):
    return 'insert $schedule isa schedule-day, has day "' + schedule["schedule"] + '";'


def museum_location_template(museum_location):
    typeql_insert_query = 'match $museum isa museum, has place-name "' + \
        museum_location["name"] + '";'
    typeql_insert_query += ' $city isa city, has place-name "' + \
        museum_location["city"] + '";'
    typeql_insert_query += ' insert (contains: $museum, falls-within: $city) isa location;'
    return typeql_insert_query


def museum_category_template(museum_category):
    typeql_insert_query = 'match $museum isa museum, has place-name "' + \
        museum_category["name"] + '";'
    typeql_insert_query += ' $category isa museum-category, has category-name "' + \
        museum_category["category"] + '";'
    typeql_insert_query += ' insert (has-museum: $museum, has-category: $category) isa museum-categories;'
    return typeql_insert_query


def museum_address_template(museum_address):
    typeql_insert_query = 'match $museum isa museum, has place-name "' + \
        museum_address["name"] + '";'
    typeql_insert_query += ' $address isa address, has address-text "' + \
        museum_address["address"] + '";'
    typeql_insert_query += ' insert (has-museum: $museum, has-address: $address) isa addresses;'
    return typeql_insert_query


def museum_coordinate_template(museum_coordinate):
    typeql_insert_query = 'match $museum isa museum, has place-name "' + \
        museum_coordinate["name"] + '";'
    typeql_insert_query += ' $coordinate isa coordinate'
    typeql_insert_query += ', has latitude ' + museum_coordinate["latitude"] + ''
    typeql_insert_query += ', has longitude ' + museum_coordinate["longitude"] + ';'
    typeql_insert_query += ' insert (has-museum: $museum, has-coordinate: $coordinate) isa coordinates;'
    return typeql_insert_query


def museum_transportation_template(museum_transportation):
    typeql_insert_query = 'match $museum isa museum, has place-name "' + \
        museum_transportation["name"] + '";'
    typeql_insert_query += ' $transportation isa transportation, has place-name "' + museum_transportation["public_transportation"] + '";'
    typeql_insert_query += ' insert (has-museum: $museum, has-transportation: $transportation) isa transportations'
    typeql_insert_query += ', has distance ' + \
        museum_transportation["distance_to_museum"] + ';'

    return typeql_insert_query


def museum_ticket_1_template(museum_ticket_1):
    typeql_insert_query = 'match $museum isa museum, has place-name "' + \
        museum_ticket_1["name"] + '";'
    typeql_insert_query += '$ticket-category isa ticket-category, has category-name "ticket 1";'
    typeql_insert_query += ' $ticket-type isa ticket-type, has ticket-name "' + \
        museum_ticket_1["ticket_1"] + '";'
    typeql_insert_query += ' insert (has-museum: $museum, has-ticket-category: $ticket-category) isa ticket-categories;'
    typeql_insert_query += ' (has-ticket-type: $ticket-type, has-ticket-category: $ticket-category) isa ticket-types'
    typeql_insert_query += ', has price ' + \
        museum_ticket_1['ticket_price_1'] + ';'
    return typeql_insert_query


def museum_ticket_2_template(museum_ticket_2):
    typeql_insert_query = 'match $museum isa museum, has place-name "' + \
        museum_ticket_2["name"] + '";'
    typeql_insert_query += '$ticket-category isa ticket-category, has category-name "ticket 2";'
    typeql_insert_query += ' $ticket-type isa ticket-type, has ticket-name "' + \
        museum_ticket_2["ticket_2"] + '";'
    typeql_insert_query += ' insert (has-museum: $museum, has-ticket-category: $ticket-category) isa ticket-categories'
    typeql_insert_query += ', has alt-name "' + museum_ticket_2["ticket_name_2"] + '";'
    typeql_insert_query += ' (has-ticket-type: $ticket-type, has-ticket-category: $ticket-category) isa ticket-types'
    typeql_insert_query += ', has price ' + \
        museum_ticket_2['ticket_price_2'] + ';'
    return typeql_insert_query


def museum_schedule_1_template(museum_schedule_1):
    typeql_insert_query = 'match $museum isa museum, has place-name "' + \
        museum_schedule_1["name"] + '";'
    typeql_insert_query += ' $schedule-category isa schedule-category, has category-name "schedule 1";'
    typeql_insert_query += ' $schedule-day isa schedule-day, has day "' + \
        museum_schedule_1["schedule_1"] + '";'
    typeql_insert_query += ' insert (has-museum: $museum, has-schedule-category: $schedule-category) isa schedule-categories'

    if "schedule_name_1" in museum_schedule_1:
        typeql_insert_query += ', has alt-name "' + \
            museum_schedule_1["schedule_name_1"] + '"'

    if museum_schedule_1["open_1"] != "" and museum_schedule_1["closed_1"] != "":
        schedule_open = museum_schedule_1["open_1"].replace(":", "") 
        schedule_closed = museum_schedule_1["closed_1"].replace(":", "")
        typeql_insert_query += ', has open ' + schedule_open + ''
        typeql_insert_query += ', has closed ' + schedule_closed + ''

    typeql_insert_query += '; (has-schedule-day: $schedule-day, has-schedule-category: $schedule-category) isa schedule-days;'
    return typeql_insert_query


def museum_schedule_2_template(museum_schedule_2):
    typeql_insert_query = 'match $museum isa museum, has place-name "' + \
        museum_schedule_2["name"] + '";'
    typeql_insert_query += ' $schedule-category isa schedule-category, has category-name "schedule 2";'
    typeql_insert_query += ' $schedule-day isa schedule-day, has day "' + \
        museum_schedule_2["schedule_2"] + '";'
    typeql_insert_query += ' insert (has-museum: $museum, has-schedule-category: $schedule-category) isa schedule-categories'

    if "schedule_name_2" in museum_schedule_2:
        typeql_insert_query += ', has alt-name "' + \
            museum_schedule_2["schedule_name_2"] + '"'

    if museum_schedule_2["open_2"] != "" and museum_schedule_2["closed_2"] != "":
        schedule_open = museum_schedule_2["open_2"].replace(":", "") 
        schedule_closed = museum_schedule_2["closed_2"].replace(":", "")
        typeql_insert_query += ', has open ' + schedule_open + ''
        typeql_insert_query += ', has closed ' + schedule_closed + ''
    
    typeql_insert_query += '; (has-schedule-day: $schedule-day, has-schedule-category: $schedule-category) isa schedule-days;'
    return typeql_insert_query


def museum_schedule_3_template(museum_schedule_3):
    typeql_insert_query = 'match $museum isa museum, has place-name "' + \
        museum_schedule_3["name"] + '";'
    typeql_insert_query += ' $schedule-category isa schedule-category, has category-name "schedule 3";'
    typeql_insert_query += ' $schedule-day isa schedule-day, has day "' + \
        museum_schedule_3["schedule_3"] + '";'
    typeql_insert_query += ' insert (has-museum: $museum, has-schedule-category: $schedule-category) isa schedule-categories'

    if "schedule_name_3" in museum_schedule_3:
        typeql_insert_query += ', has alt-name "' + \
            museum_schedule_3["schedule_name_3"] + '"'

    if museum_schedule_3["open_3"] != "" and museum_schedule_3["closed_3"] != "":
        schedule_open = museum_schedule_3["open_3"].replace(":", "") 
        schedule_closed = museum_schedule_3["closed_3"].replace(":", "")
        typeql_insert_query += ', has open ' + schedule_open + ''
        typeql_insert_query += ', has closed ' + schedule_closed + ''

    typeql_insert_query += '; (has-schedule-day: $schedule-day, has-schedule-category: $schedule-category) isa schedule-days;'
    return typeql_insert_query


dir_path = os.getcwd()
# file path & functions for inserting data to knowledge graph
inputs = [
    {
        "data_path": dir_path + "/datasets/split_dataset/museum",
        "template": museum_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/city",
        "template": city_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/coordinate",
        "template": coordinate_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/address",
        "template": address_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/category",
        "template": category_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/transportation",
        "template": transportation_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/transportation_type",
        "template": transportation_type_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/ticket_category",
        "template": ticket_category_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/ticket_type",
        "template": ticket_type_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/schedule_category",
        "template": schedule_category_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/schedule_day",
        "template": schedule_day_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/museum_location",
        "template": museum_location_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/museum_category",
        "template": museum_category_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/museum_address",
        "template": museum_address_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/museum_coordinate",
        "template": museum_coordinate_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/museum_transportation",
        "template": museum_transportation_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/museum_ticket_1",
        "template": museum_ticket_1_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/museum_ticket_2",
        "template": museum_ticket_2_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/museum_schedule_1",
        "template": museum_schedule_1_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/museum_schedule_2",
        "template": museum_schedule_2_template
    },
    {
        "data_path": dir_path + "/datasets/split_dataset/museum_schedule_3",
        "template": museum_schedule_3_template
    },
]

build_museum_recsys_chatbot_graph(inputs)
