import pandas as pd
import sqlite3

csv_path = 'data/Billionaires.csv'
db_path = 'data/Billionaires.db'




create_tables = [
    """
    CREATE TABLE IF NOT EXISTS Continents (
        id INTEGER PRIMARY KEY,
        continent TEXT
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS Countries (
        id INTEGER PRIMARY KEY,
        cpi_country NUMERIC,
        cpi_change_country NUMERIC,
        gdp_country NUMERIC,
        g_tertiary_ed_enroll NUMERIC,
        g_primary_ed_enroll NUMERIC,
        life_expectancy NUMERIC,
        tax_revenue NUMERIC,
        tax_rate NUMERIC,
        country_pop NUMERIC,
        country_lat NUMERIC,
        country_long NUMERIC,
        continent_id INTEGER REFERENCES Continents (id)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS Industries (
        id INTEGER PRIMARY KEY,
        industry TEXT,
        source TEXT
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS People (
        id INTEGER PRIMARY KEY,
        position INTEGER,
        wealth INTEGER,
        full_name TEXT,
        age INTEGER,
        citizenship TEXT,
        gender TEXT,
        birth_date NUMERIC,
        last_name TEXT,
        first_name TEXT,
        birth_year INTEGER,
        birth_month NUMERIC,
        birth_day INTEGER,
        residence_id INTEGER REFERENCES Residences (id),
        industry_id INTEGER REFERENCES Industries (id)
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS Residences (
        id INTEGER PRIMARY KEY,
        country_of_residence TEXT,
        city_of_residence TEXT,
        residence_state TEXT,
        residence_region TEXT,
        country_id INTEGER REFERENCES Countries (id)
    );
    """
]



insert_queries = [
    """
    INSERT INTO Continents (continent)
    SELECT DISTINCT continent
    FROM temp_table;
    """,


    """
    INSERT INTO Countries (
        cpi_country, cpi_change_country, gdp_country, g_tertiary_ed_enroll, 
        g_primary_ed_enroll, life_expectancy, tax_revenue, tax_rate, country_pop, country_lat, 
        country_long, continent_id
    )
    SELECT DISTINCT
        t.cpi_country, t.cpi_change_country, t.gdp_country, t.g_tertiary_ed_enroll,
        t.g_primary_ed_enroll, t.life_expectancy, t.tax_revenue, t.tax_rate, t.country_pop, t.country_lat, 
        t.country_long,
        c.id
    FROM temp_table t
    JOIN Continents c ON t.continent = c.continent;
    """,

    # Insert into Industries
    """
    INSERT INTO Industries (industry, source)
    SELECT DISTINCT industry, source
    FROM temp_table;
    """,

    """
    INSERT INTO Residences (
        country_of_residence, city_of_residence, residence_state, 
        residence_region, country_id
    )
    SELECT DISTINCT
        t.country_of_residence, t.city_of_residence, t.residence_state, 
        t.residence_region,
        c.id
    FROM temp_table t
    JOIN Countries c ON t.cpi_country = c.cpi_country AND t.country_lat = c.country_lat;
    """,


    """
    INSERT INTO People (
        position, wealth, full_name, age, citizenship, gender, birth_date, 
        last_name, first_name, birth_year, birth_month, birth_day, 
        residence_id, industry_id
    )
    SELECT
        t.position, t.wealth, t.full_name, t.age, t.citizenship, t.gender, 
        t.birth_date, t.last_name, t.first_name, t.birth_year, t.birth_month, 
        t.birth_day,
        r.id,
        i.id
    FROM temp_table t
    JOIN Residences r ON t.country_of_residence = r.country_of_residence AND t.city_of_residence = r.city_of_residence
    JOIN Industries i ON t.industry = i.industry AND t.source = i.source;
    """
]




def import_csv_to_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for table_sql in create_tables:
        cursor.execute(table_sql)

    data = pd.read_csv(csv_path)



    data.to_sql('temp_table', conn, if_exists='replace', index=False)


    for query in insert_queries:
        cursor.execute(query)


    cursor.execute("DROP TABLE IF EXISTS temp_table;")
    print("Temporary table dropped.")


    conn.commit()
    conn.close()

    print("CSV data imported into the permanent tables and tables set up successfully!")


def count_rows_in_all_tables():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print("Contagem de registros em todas as tabelas:")

        # para cada tabela conta as linhas
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0] #retorna o numero obtido pela query
            print(f"Tabela {table_name}: {count} registros.")

    except sqlite3.Error as e:
        print(f"Erro ao contar registros: {e}")

    conn.close()




def execute_query_and_print(query):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(query)

    column_names = [description[0] for description in cursor.description] #extrai os nomes das colunas e retorna informações sobre as colunas do resultado da query
    print(column_names)


    results = cursor.fetchall()


    for row in results:
        print(row)

    conn.close()
    for row in results:
        print(row)

    conn.close()
