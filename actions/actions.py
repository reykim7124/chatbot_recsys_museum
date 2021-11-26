# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
# #
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher


# class ActionHelloWorld(Action):

#     def name(self) -> Text:
#         return "action_hello_world"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         dispatcher.utter_message(text="Hello World!")

#         return []

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from typing import Text, Dict, Any
from rasa_sdk.executor import CollectingDispatcher
from scripts.GraphDatabase import GraphDatabase


class ActionSubmitForm(Action):

    def name(self) -> Text:
        return "action_submit_form"


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        graph_database = GraphDatabase()
        # entity_type = "museum"

        attributes = {
            "schedule_day": tracker.get_slot("schedule_day"),
            "ticket_price": tracker.get_slot("ticket_price"),
            "use_public_transport": tracker.get_slot("use_public_transport")
        }

        # entities = graph_database.get_entities(entity_type, attributes)
        entities = graph_database.get_entities(attributes)

        slots = [SlotSet("recommendations", entities)]
        
        for key in attributes:
            slots.append(SlotSet(key, None))

        return slots


class ActionQueryEntities(Action):

    def name(self):
        return "action_query_entities"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        listed_items = tracker.get_slot("listed_items")
        entities = tracker.get_slot("recommendations")
        slots = []

        if not listed_items or listed_items[-1]["id"] == 15:
            slots.append(SlotSet("listed_items", entities[:5]))
        else:
            last_item = listed_items[-1]["id"]
            slots.append(SlotSet("listed_items", entities[last_item:last_item + 5]))

        return slots


class ActionListEntities(Action):
    def name(self):
        return "action_list_entities"

    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        dispatcher.utter_message(
            "Berikut daftar rekomendasi museum:"
        )
        
        entities = tracker.get_slot("listed_items")

        for i, e in enumerate(entities):
            dispatcher.utter_message(f"{i + 1}: {e['name']}")

        return []