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

        if entities is None:
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

        if entities is None:
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

        if entities is None:
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
                "terakhir": lambda l: l[-1],
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
        
        utter_description = "Deskripsi {0}\n\n{1}".format(query["name"], query["description"])

        utter_text = "Informasi {}:\n".format(query["name"])
        utter_text += "Kategori: {}\n\n".format(query["category"])
        utter_text += "\nKontak:\n"

        phone_number = query["phone-number"].split(", ")
        if len(phone_number) > 1:
            utter_text += "No. Telpon:\n"
            for p in phone_number:
                utter_text += "- {}\n".format(str(p))
        else:
            utter_text += "No. Telpon: {}\n".format(str(phone_number[0]))

        if query["email"] != "":
            email = query["email"].split(", ")
            for e in email:
                if len(email) > 1:
                    utter_text += "\nEmail:\n"
                    utter_text += "- {}\n".format(e)
                else:
                    utter_text += "Email: {}\n".format(e)

        if query["website"]:
            utter_text += 'Website: {}\n'.format(query["website"])

        utter_text += "\n"

        if query["facebook"] or query["instagram"] or query["twitter"]:
            utter_text += 'Sosial Media:\n'
            if query["facebook"] != "":
                utter_text += "- Facebook: {}\n".format(query["facebook"])

            if query["instagram"] != "":
                utter_text += "- Instagram: {}\n".format(query["instagram"])

            if query["twitter"] != "":
                utter_text += "- Twitter: {}\n".format(query["twitter"])

        utter_text += "\n"
        utter_text += "\nDaftar Jadwal:\n"
        if query["name"] == "Museum BNI 1946":
            utter_text += "- Wajib Reservasi Terlebih Dahulu\n"
        else:
            for key, value in query["schedule"].items():
                open_time = str(int(value["open"]))
                closed_time = str(int(value["closed"]))
                x = lambda a : a[:2] if len(a) == 4 else a[:1]
                y = lambda a : a[2:] if len(a) == 4 else a[1:]
                utter_text += 'Jadwal {}:\n'.format(key[-1])
                if value["alt-name"] != "":
                    utter_text += "- Nama: {}\n".format(value["alt-name"])
                utter_text += "- Buka dari jam {0}:{1} - ".format(x(open_time), y(open_time))
                utter_text += "{0}:{1}\n".format(x(closed_time), y(closed_time))
                utter_text += "- Di hari "

                for day in value["schedule-day"]:
                    d = "{}, ".format(day)
                    if day == value["schedule-day"][-1]:
                        d = "{}\n".format(day)

                    utter_text += d

        utter_text += '\n\nKategori Tiket:\n'
        for key, value in query["ticket"].items():
            utter_text += "Tiket {}:\n".format(key[-1])

            if value["alt-name"] != "":
                utter_text += "- Nama lain kategori tiket {0}: {1}\n".format(key[-1], value["alt-name"])

            utter_text += "- Daftar Tiket:\n"

            for i in value["ticket-type"]:
                price = i["price"]
                if price > 0:
                    price = "harga Rp {:,.0f}".format(price)
                    price.replace(",", ".")
                else:
                    price = "Gratis"

                utter_text += "&nbsp;&nbsp;&nbsp;&nbsp;- Tiket {0}, {1}\n".format(i["ticket-name"], price)
            
            utter_text += "\n\n"

        utter_text += "\nAlamat:\n"
        utter_text += "- Jalan: {}\n".format(query["address"])
        utter_text += "- Kota: {}\n".format(query["city"])
        utter_text += "- Google Map: [Klik Disini](https://maps.google.com/?q={0},{1})\n".format(str(query["latitude"]), str(query["longitude"]))
        
        utter_text += '\n\nTransportasi Umum:\n'
        for value in query["transportation"]:
            if value["distance"] < 1:
                dist = 0
                dist = value["distance"] * 1000
                utter_text += "- {} m ".format(str(dist))
            else:
                utter_text += "- {} Km ".format(str(value["distance"]))

            utter_text += "dari {}\n".format(value["transportation"])

        dispatcher.utter_message(text=utter_description)
        dispatcher.utter_message(text=utter_text)

        return [SlotSet("museum", None)]
