from typedb.client import TypeDB, SessionType, TransactionType
import os


def build_museum_recsys_chatbot_graph(inputs):
    with TypeDB.core_client("localhost:1729") as client:
        with client.session("phone_calls", SessionType.DATA) as session:
            for input in inputs:
                print(
                    "Loading from [" + input["data_path"] + "] into TypeDB ...")
                load_data_into_typedb(input, session)


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
        "data_path": dir_path + "/datasets/entry_ticket",
        "template": entry_ticket_template
    },
    {
        "data_path": dir_path + "/datasets/other_ticket",
        "template": other_ticket_template
    },
    {
        "data_path": dir_path + "/datasets/museum_location",
        "template": museum_location_template
    },
    {
        "data_path": dir_path + "/datasets/museum_transportation",
        "template": museum_transportation_template
    },
    {
        "data_path": dir_path + "/datasets/museum_entry_ticket",
        "template": museum_entry_ticket_template
    },
    {
        "data_path": dir_path + "/datasets/museum_other_ticket",
        "template": museum_other_ticket_template
    }
]

build_museum_recsys_chatbot_graph(inputs)
