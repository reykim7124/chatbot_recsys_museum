from typedb.client import TypeDB, SessionType, TransactionType, TypeDBOptions

with TypeDB.core_client("localhost:1729") as client:
    with client.session("museum_recsys_chatbot", SessionType.DATA) as session:
        options = TypeDBOptions.core()
        options.infer = True
        with session.transaction(TransactionType.READ, options) as read_transaction:
            answer_iterator = read_transaction.query().match('match $m isa museum, has place-name $mpn;' + \
            '$sd1 isa schedule-day, has day "Senin";' + \
            '$sd2 isa schedule-day, has day "Rabu";' + \
            '$sd3 isa schedule-day, has day "Sabtu";' + \
            '(has-museum: $m, has-schedule-day: $sd1) isa schedule-days;' + \
            '(has-museum: $m, has-schedule-day: $sd2) isa schedule-days;' + \
            '(has-museum: $m, has-schedule-day: $sd3) isa schedule-days;' + \
            '$sc isa schedule-category;' + \
            '$scs (has-museum: $m, has-schedule-category: $sc) isa schedule-categories;' + \
            '$scs has open $o;' + \
            '$scs has closed $c;' +\
            '$o > 700;' + \
            '$c <= 1500;' + \
            'get $m, $sd1, $sd2, $sd3, $mpn, $sc, $o, $c;' + \
            'offset 0;' + \
            'limit 5;')

            for answer in answer_iterator:
                museum = answer.get("mpn")
                print("Retrieved museum with name " + museum.get_value())