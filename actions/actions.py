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
from rasa_sdk.events import SlotSet, AllSlotsReset
from typing import Text, Dict, Any
from rasa_sdk.executor import CollectingDispatcher
from scripts.GraphDatabase import GraphDatabase


class ActionResetAllSlot(Action):
    def name(self) -> Text:
        return "action_reset_all_slot"


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        return [AllSlotsReset()]

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
        
        if entities is None:
            return [SlotSet("recommendations", None)]

        slots = [SlotSet("recommendations", entities)]
        
        for key in attributes:
            slots.append(SlotSet(key, None))

        return slots


class ActionQueryEntities(Action):

    def name(self) -> Text:
        return "action_query_entities"


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        entities = tracker.get_slot("recommendations")

        if len(entities) <= 0:
            return []

        listed_items = tracker.get_slot("listed_items")
        slots = []

        if not listed_items or listed_items[-1]["id"] == 15:
            slots.append(SlotSet("listed_items", entities[:5]))
        else:
            last_item = listed_items[-1]["id"]
            slots.append(SlotSet("listed_items", entities[last_item:last_item + 5]))

        return slots


class ActionListEntities(Action):
    def name(self) -> Text:
        return "action_list_entities"

    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        entities = tracker.get_slot("listed_items")

        if len(entities) <= 0:
            return []

        dispatcher.utter_message(
            "Berikut daftar rekomendasi museum:"
        )
        
        for i, e in enumerate(entities):
            dispatcher.utter_message(f"{i + 1}: {e['name']}")

        return []


class ActionResolveMention(Action):
    def name(self) -> Text:
        return "action_resolve_mention"


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        entities = tracker.get_slot("listed_items")

        if len(entities) <= 0:
            return []

        mention = tracker.get_slot("mention")
        value = None
        if mention is not None:
            mentions = {
                "1": lambda l: l[0],
                "2": lambda l: l[1],
                "3": lambda l: l[2],
                "4": lambda l: l[3],
                "5": lambda l: l[4],
                # "ANY": lambda l: random.choice(l),
                "LAST": lambda l: l[-1],
            }

            fx = mentions[mention]
            value = fx(entities)
            return [
                SlotSet("museum", value["name"]), 
                SlotSet("mention", None)
            ]

        return []


class ActionQueryMuseum(Action):
    def name(self) -> Text:
        return "action_query_museum"


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]):
        museum = tracker.get_slot("museum")

        if museum is None:
            return []

        graph_database = GraphDatabase()
        query = graph_database.get_entity(museum)
        utter_text = f'''
            Informasi {query["name"]}:
            Kategori: {query["category"]}
            Kontak:
        '''

        phone_number = query["phone-number"].split(", ") if len(query["phone-number"]) > 0 else query["phone-number"]

        if phone_number is list:
            utter_text += '- No. Telpon:\n'
            for p in phone_number:
                utter_text += f"- {p}\n"
        else:
            utter_text += f'- No. Telpon: {phone_number}\n'

        if query["email"]:
            email = query["email"].split(", ") if len(query["email"]) > 0 else query["email"]
            if email is list:
                utter_text += '- Email:\n'
                for e in email:
                    utter_text += f"- {e}\n"
            else:
                utter_text += f'- Email: {email}\n'

        if query["website"]:
            utter_text += f'- Website: {query["website"]}\n'

        utter_text += "\n\n"

        if query["facebook"] or query["instagram"] or query["twitter"]:
            utter_text += f'''Sosial Media:
                {"- Facebook: " + query["facebook"] if query["facebook"] else ""}
                {"- Instagram: " + query["instagram"] if query["instagram"] else ""}
                {"- Twitter: " + query["twitter"] if query["twitter"] else ""}
                

            '''

        utter_text += 'Daftar Jadwal:\n'
        for key, value in query["schedule"].items():
            open_time = str(value["open"])
            closed_time = str(value["closed"])
            x = lambda a : a[:2] if len(a) == 4 else a[:1]
            y = lambda a : a[2:] if len(a) == 4 else a[1:]
            utter_text += f'''- Jadwal {key[-1]}:
                {"- Nama: " + value["alt-name"] if value["alt-name"] else ""}
                - Buka dari jam {"{0}:{1}".format(x(open_time), y(open_time))} - {"{0}:{1}".format(x(closed_time), y(closed_time))}
                - Setiap hari {value["schedule-day"][0]} - {value["schedule-day"][-1]}
                
                
            '''
     
        utter_text += 'Kategori Tiket:\n'
        for key, value in query["ticket"].items():
            utter_text += f'- Daftar Tiket {key[-1]}:'

            for i in value["ticket-type"]:
                utter_text += f'''
                    - Tiket {i["ticket-name"]}, harga {str(i["price"])}
                '''
            
            utter_text += f'{"- Nama lain kategori tiket {key[-1]}: " + value["alt-name"] if value["alt-name"] else ""}'

        utter_text += "\n\n"

        utter_text += f'''Alamat:
            - Jalan: {query["address"]}
            - Kota: {query["city"]}
            - Google Map: [Klik Disini](https://maps.google.com/?q={str(query["latitude"])},{str(query["longitude"])})\n
        '''
        utter_text += "\n\n"
        utter_text += 'Transportasi Umum:\n'

        for value in query["transportation"]:
            utter_text += f'- {str(value["distance"])} Km dari {value["transportation"]}'

        print(utter_text)
        dispatcher.utter_message(text="test")

        return [SlotSet("museum", None)]
