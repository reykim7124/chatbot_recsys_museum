from typedb.client import TypeDB, SessionType, TransactionType, TypeDBOptions
from pprint import pprint
with TypeDB.core_client("localhost:1729") as client:
    with client.session("museum_recsys_chatbot", SessionType.DATA) as session:
        options = TypeDBOptions.core()
        options.infer = True
        with session.transaction(TransactionType.READ, options) as read_transaction:
            answer_iterator = read_transaction.query().match('match $m isa museum, has place-name $mpn, has facebook $fb;' + \
            '$sd1 isa schedule-day, has day "Senin";' + \
            '$sd2 isa schedule-day, has day "Rabu";' + \
            '$sd3 isa schedule-day, has day "Sabtu";' + \
            '(has-museum: $m, has-schedule-day: $sd1) isa schedule-days;' + \
            '(has-museum: $m, has-schedule-day: $sd2) isa schedule-days;' + \
            '(has-museum: $m, has-schedule-day: $sd3) isa schedule-days;' + \
            'get $mpn, $fb;' + \
            'offset 0;' + \
            'limit 3;')

            for answer in answer_iterator:
                # museum = answer
                # print("Retrieved museum with name " + museum.get_value();
                pprint(vars(answer))
                # for ans in answer.map():
                #     print(ans)