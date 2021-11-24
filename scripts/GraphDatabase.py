from typing import Any, Text, Dict, List, Optional
from typedb.client import TypeDB, SessionType, TransactionType, TypeDBOptions
from scripts import Recommender

class KnowledgeBase(object):

    def get_entities(
        self,
        entity_type: Text,
        attributes: Optional[List[Dict[Text, Text]]] = None,
        limit: int = 5,
    ) -> List[Dict[Text, Any]]:

        raise NotImplementedError("Method is not implemented.")

    def get_attribute_of(
        self, entity_type: Text, key_attribute: Text, entity: Text, attribute: Text
    ) -> List[Any]:

        raise NotImplementedError("Method is not implemented.")

    def validate_entity(
        self, entity_type, entity, key_attribute, attributes
    ) -> Optional[Dict[Text, Any]]:

        raise NotImplementedError("Method is not implemented.")

    def map(self, mapping_type: Text, mapping_key: Text) -> Text:

        raise NotImplementedError("Method is not implemented.")


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
                    # concepts = result_iter.concepts()
                    for i, c in enumerate(result_iter):
                        entities.append(self._thing_to_dict(i, c))
                    return entities
    

    def _get_museum_entity(
        self, attributes: List[Dict[Text, Text]]
    ) -> List[Dict[Text, Any]]:
        schedule_day = attributes["schedule_day"]
        ticket_price = attributes["ticket_price"]
        use_public_transport = attributes["use_public_transport"]
        query = "match $m isa museum, has place-name $name;"
        
        if (use_public_transport == "kendaraan umum" or use_public_transport == "tidak pakai kendaraan"):
            query += "$t isa transportation; (has-transportation: $t, has-museum: $m) isa transportations, has distance < 15;"

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

        query += "get $name; offset 0; limit 1;"

        return self._execute_entity_query(query)

    
    def get_entities(
        self,
        entity_type: Text,
        attributes: Optional[List[Dict[Text, Text]]] = None,
        limit: int = 10,
    ) -> List[Dict[Text, Any]]:
        if entity_type == "museum":
            entity = self._get_museum_entity(attributes)
            recommender = Recommender.Recommender()
            return recommender.knn(entity[0]["name"])


# graph = GraphDatabase()
# attributes = {
#     "schedule_day": ["senin", "selasa"],
#     "ticket_price": ["0", "50000"],
#     "use_public_transport": "kendaraan umum"
# }
# get_graph = graph.get_entities(entity_type="museum", attributes=attributes, limit=5)
# print(get_graph)