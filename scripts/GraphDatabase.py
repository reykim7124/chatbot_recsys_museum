from typing import Any, Text, Dict, List, Optional
from typedb.client import TypeDB, SessionType, TransactionType, TypeDBOptions
# from scripts import Recommender
from Recommender import Recommender

class KnowledgeBase(object):

    def get_entities(
        self,
        attributes: Optional[List[Dict[Text, Text]]] = None,
        limit: int = 5,
    ) -> List[Dict[Text, Any]]:

        raise NotImplementedError("Method is not implemented.")


    def get_entity(
        self, 
        object_identifier: Text
    ) -> Optional[Dict[Text, Any]]:
        raise NotImplementedError("Method is not implemented.")


    # def get_attribute_of(
    #     self, key_attribute: Text, entity: Text, attribute: Text
    # ) -> List[Any]:

    #     raise NotImplementedError("Method is not implemented.")


    # def validate_entity(
    #     self, entity, key_attribute, attributes
    # ) -> Optional[Dict[Text, Any]]:

    #     raise NotImplementedError("Method is not implemented.")


    # def map(self, mapping_type: Text, mapping_key: Text) -> Text:

    #     raise NotImplementedError("Method is not implemented.")


class GraphDatabase(KnowledgeBase):
    def __init__(self, uri: Text = "localhost:1729", database: Text = "museum_recsys_chatbot"):
        self.uri = uri
        self.database = database


    def _thing_to_dict(self, idx, thing):
        """
        Converts a thing (a typedb object) to a dict for easy retrieval of the thing's
        attributes.
        """
        entity = {"id": idx}
        for each in thing.map():
            entity[each] = thing.get(each).get_value()
        return entity


    def _execute_entity_query(self, query: Text) -> List[Dict[Text, Any]]:
        """
        Executes a query that returns a list of entities with all their attributes.
        """
        with TypeDB.core_client(self.uri) as client:
            with client.session(self.database, SessionType.DATA) as session:
                options = TypeDBOptions.core()
                options.infer = True
                with session.transaction(TransactionType.READ, options) as read_transaction:
                    result_iter = read_transaction.query().match(query)
                    entities = []
                    for i, c in enumerate(result_iter):
                        entities.append(self._thing_to_dict(i + 1, c))
                    
                    return entities
    

    def _get_museum_entities(
        self, attributes: List[Dict[Text, Text]]
    ) -> List[Dict[Text, Any]]:
        schedule_day = attributes["schedule_day"]
        ticket_price = attributes["ticket_price"]
        use_public_transport = attributes["use_public_transport"]
        query = "match $m isa museum, has place-name $name;"
        
        if (use_public_transport == "kendaraan umum" or use_public_transport == "tidak pakai kendaraan"):
            query += "$t isa transportation; (has-transportation: $t, has-museum: $m) isa transportations, has distance <= 10;"

        for idx, sd in enumerate(schedule_day):
            query += f'''
                $sd{str(idx)} isa schedule-day, has day "{sd.capitalize()}";
                (has-museum: $m, has-schedule-day: $sd{str(idx)}) isa schedule-days;
            '''

        query += (
            '$tt isa ticket-type;'
            '$tts (has-museum: $m, has-ticket-type: $tt) isa ticket-types;'
            '$tts has price $p;'
        )        

        if (int(ticket_price[0]) > int(ticket_price[1])):
            query += f'''
                $p <= {ticket_price[0]};
                $p >= {ticket_price[1]};
            '''
        else:
            query += f'''
                $p >= {ticket_price[0]};
                $p <= {ticket_price[1]};
            '''

        query += "get $name; limit 5;"

        return self._execute_entity_query(query)


    def _get_museum_entity(
        self,
        object_identifier: Text
    ) -> Optional[Dict[Text, Any]]:
        if object_identifier == "Museum BNI 1946":
            query = f'''
            match $m isa museum;
            $m has place-name $name;
            $name "{object_identifier}";
            $m has phone-number $phone-number;
            $m has website $website;
            $m has facebook $facebook;
            $m has twitter $twitter;
            $m has instagram $instagram;
            $m has email $email;
            $mc isa museum-category, has category-name $category;
            (has-museum: $m, has-category: $mc) isa museum-categories;
            $a isa address, has address-text $address;
            $ad (has-museum: $m, has-address: $a) isa addresses;
            $t isa transportation, has place-name $transportation;
            (has-transportation: $t, has-museum: $m) isa transportations,
            has distance $distance;
            $co isa coordinate, has latitude $latitude, has longitude $longitude;
            (has-museum: $m, has-coordinate: $co) isa coordinates;
            $c isa city, has place-name $city;
            (contains: $m, falls-within: $c) isa location;
            $tt isa ticket-type, has ticket-name $ticket;
            (has-museum: $m, has-ticket-type: $tt) isa ticket-types,
            has price $price,
            has category-name $ticket-category,
            has alt-name $ticket-name;
            get $name, $phone-number, $website, $facebook, $twitter,
            $instagram, $email, $category, $latitude, $longitude, $city,
            $address, $transportation, $distance, $ticket, $price, $ticket-category,
            $ticket-name;
        '''
        else:
            query = f'''
                match $m isa museum;
                $m has place-name $name;
                $name "{object_identifier}";
                $m has phone-number $phone-number;
                $m has website $website;
                $m has facebook $facebook;
                $m has twitter $twitter;
                $m has instagram $instagram;
                $m has email $email;
                $mc isa museum-category, has category-name $category;
                (has-museum: $m, has-category: $mc) isa museum-categories;
                $a isa address, has address-text $address;
                $ad (has-museum: $m, has-address: $a) isa addresses;
                $t isa transportation, has place-name $transportation;
                (has-transportation: $t, has-museum: $m) isa transportations,
                has distance $distance;
                $sd isa schedule-day, has day $day;
                (has-schedule-day: $sd, has-museum: $m) isa schedule-days,
                has open $open,
                has closed $closed,
                has category-name $schedule-category,
                has alt-name $schedule-name;
                $co isa coordinate, has latitude $latitude, has longitude $longitude;
                (has-museum: $m, has-coordinate: $co) isa coordinates;
                $c isa city, has place-name $city;
                (contains: $m, falls-within: $c) isa location;
                $tt isa ticket-type, has ticket-name $ticket;
                (has-museum: $m, has-ticket-type: $tt) isa ticket-types,
                has price $price,
                has category-name $ticket-category,
                has alt-name $ticket-name;
                get $name, $phone-number, $website, $facebook, $twitter,
                $instagram, $email, $category, $latitude, $longitude, $city,
                $address, $transportation, $distance, $day, $open, $closed,
                $schedule-category, $schedule-name, $ticket, $price, $ticket-category,
                $ticket-name;
            '''
        return self._execute_entity_query(query)

    
    def get_entities(
        self,
        attributes: Optional[List[Dict[Text, Text]]] = None,
    ) -> List[Dict[Text, Any]]:
        entities = self._get_museum_entities(attributes)

        if len(entities) > 0:
            # recommender = Recommender.Recommender(attributes["use_public_transport"])
            recommender = Recommender()
            return recommender.recommend(entities)
        else:
            return None

    
    def get_entity(
        self, 
        object_identifier: Text
    ) -> Optional[Dict[Text, Any]]:
        list_of_objects = self._get_museum_entity(object_identifier)
        if len(list_of_objects) <= 0:
            return []

        entity = list_of_objects[0]
        entity["transportation"] = [{
            "transportation": entity["transportation"],
            "distance": entity.pop("distance")
        }]

        entity["ticket"] = {
            entity.pop("ticket-category"): {
                "alt-name": entity.pop("ticket-name"),
                "ticket-type": [
                    {
                        "ticket-name": entity["ticket"],
                        "price": entity.pop("price")
                    }
                ]
            }
        }

        if entity["name"] != "Museum BNI 1946":
            entity["schedule"] = {
                entity.pop("schedule-category"): {
                    "alt-name": entity.pop("schedule-name"),
                    "schedule-day": [entity.pop("day")],
                    "open": entity.pop("open"),
                    "closed": entity.pop("closed")
                },
            }

        for e in list_of_objects[1:]:
            transport = {
                "transportation": e["transportation"],
                "distance": e["distance"]
            }

            if transport not in entity["transportation"]:
                entity["transportation"].append(transport)

            if e["ticket-category"] not in entity["ticket"]:
                entity["ticket"][e["ticket-category"]] = {
                    "alt-name": e["ticket-name"],
                    "ticket-type": []
                }
            
            ticket = {
                "ticket-name": e["ticket"],
                "price": e["price"]
            }

            if ticket not in entity["ticket"][e["ticket-category"]]["ticket-type"]:
                entity["ticket"][e["ticket-category"]]["ticket-type"].append(ticket)

            if entity["name"] != "Museum BNI 1946":
                if e["schedule-category"] not in entity["schedule"]:
                    entity["schedule"][e["schedule-category"]] = {
                        "alt-name": e["schedule-name"],
                        "open": e["open"],
                        "closed": e["closed"],
                        "schedule-day": []
                    }

                if e["day"] not in entity["schedule"][e["schedule-category"]]["schedule-day"]:
                    entity["schedule"][e["schedule-category"]]["schedule-day"].append(e["day"])
            
        return entity


# graph = GraphDatabase()
# attributes = {
#     "schedule_day": ["senin", "selasa"],
#     "ticket_price": ["0", "50000"],
#     "use_public_transport": "kendaraan umum"
# }
# get_graph = graph.get_entities(attributes=attributes)
# get_graph = graph.get_entity("Art: 1 New Museum")
# print(get_graph)