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
from typing import Text, Dict, Any, List
from rasa_sdk.executor import CollectingDispatcher
from scripts.GraphDatabase import GraphDatabase
# from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase

class ActionQueryEntities(Action):
    """Action for listing entities.
    The entities might be filtered by specific attributes."""

    def name(self):
        return "action_query_entities"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        graph_database = GraphDatabase()

        # first need to know the entity type we are looking for
        # entity_type = get_entity_type(tracker)
        entity_type = "museum"

        if entity_type is None:
            dispatcher.utter_template("utter_rephrase", tracker)
            return []

        # check what attributes the NER found for entity type
        # attributes = get_attributes_of_entity(entity_type, tracker)
        attributes = {
            "schedule_day": tracker.get_slot("schedule_day"),
            "ticket_price": tracker.get_slot("ticket_price"),
            "use_public_transport": tracker.get_slot("use_public_transport")
        }

        # query knowledge base
        entities = graph_database.get_entities(entity_type, attributes)

        # filter out transactions that do not belong the set account (if any)
        # if entity_type == "transaction":
        #     account_number = tracker.get_slot("account")
        #     entities = self._filter_transaction_entities(entities, account_number)

        if not entities:
            dispatcher.utter_template(
                "I could not find any entities for '{}'.".format(entity_type), tracker
            )
            return []

        # utter a response that contains all found entities
        # use the 'representation' attributes to print an entity
        # entity_representation = schema[entity_type]["representation"]

        dispatcher.utter_message(
            "Found the following '{}' entities:".format(entity_type)
        )
        # sorted_entities = sorted([to_str(e, entity_representation) for e in entities])
        for i, e in enumerate(entities):
            dispatcher.utter_message(f"{i + 1}: {e['name']}")

        return []

        # set slots
        # set the entities slot in order to resolve references to one of the found
        # entites later on
        # entity_key = schema[entity_type]["key"]

        # slots = [
        #     SlotSet("entity_type", entity_type),
        #     SlotSet("listed_items", list(map(lambda x: to_str(x, entity_key), entities))),
        # ]

        # if only one entity was found, that the slot of that entity type to the
        # found entity
        # if len(entities) == 1:
        #     slots.append(SlotSet(entity_type, to_str(entities[0], entity_key)))

        # reset_attribute_slots(slots, entity_type, tracker)

        # return slots