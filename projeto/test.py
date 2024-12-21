from utils import import_csv_to_db, execute_query_and_print
import os


if __name__ == '__main__':
    if not os.path.exists('data/Billionaires.db'):
        import_csv_to_db()

    query = ("select * from people where position = 591")
    execute_query_and_print(query)

