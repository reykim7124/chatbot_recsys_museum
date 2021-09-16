from typedb.client import TypeDB 
import os

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