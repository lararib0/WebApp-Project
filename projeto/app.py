from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
db_path = "data/Billionaires.db"

def execute_query(query, params=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query, params or [])
    columns = [description[0] for description in cursor.description]
    results = cursor.fetchall()
    conn.close()
    return columns, results

@app.route("/")
def home():

    total_query = "SELECT COUNT(DISTINCT full_name) FROM people"
    total_industry_query = "SELECT COUNT(DISTINCT industry_id) FROM people"
    total_country_query = "SELECT COUNT(DISTINCT country_id) FROM residences"
    total_continent_query = "SELECT COUNT(DISTINCT continent_id) FROM countries"

    _, total_result = execute_query(total_query)
    _, total_industry_query = execute_query(total_industry_query)
    _, total_country_query = execute_query(total_country_query)
    _, total_continent_query = execute_query(total_continent_query)


    total_billionaires = total_result[0][0] if total_result else 0
    industry = round(total_industry_query[0][0], 2) if total_industry_query[0][0] else 0
    country = round(total_country_query[0][0], 2) if total_country_query[0][0] else 0
    continent = round(total_continent_query[0][0], 2) if total_continent_query[0][0] else 0


    return render_template(
        "index.html",
        total_billionaires=total_billionaires,
        industry=industry,
        country=country,
        continent=continent,
    )


@app.route("/search", methods=["POST"])
def search():
    search_term = request.form.get("search_term", "").strip()
    if not search_term:
        return render_template(
            "results.html",
            results=[],
            message="Por favor, insira um termo para pesquisa.",
            search_term=search_term,
        )
    query = """
        SELECT id, full_name, age, position, wealth
        FROM people
        WHERE full_name LIKE ?
        ORDER BY full_name ASC
    """
    params = [f"{search_term}%"]
    columns, results = execute_query(query, params)
    return render_template(
        "results.html",
        results=results,
        message=None if results else "Nenhum resultado encontrado.",
        search_term=search_term,
        total_billionaires=0,
        percentage=0,
        total_billionaires_in_database=0,
    )

@app.route("/search_by_id", methods=["POST"])
def search_by_id():
    billionaire_id = request.form.get("id", "").strip()

    if not billionaire_id.isdigit():
        return render_template(
            "results.html",
            results=[],
            message="Por favor, insira um número válido para o ID.",
            search_term=billionaire_id,
            total_billionaires=0,
            percentage=0,
            total_billionaires_in_database=0,
        )

    query = """
        SELECT id, full_name, age, position, wealth
        FROM people
        WHERE id = ?
    """
    params = [int(billionaire_id)]
    columns, results = execute_query(query, params)

    return render_template(
        "results.html",
        results=results,
        message=None if results else "Nenhum bilionário encontrado para este ID.",
        search_term=billionaire_id,
        total_billionaires=0,
        percentage=0,
        total_billionaires_in_database=0,
    )

@app.route("/all_by_id")
def all_billionaires_by_id():
    query = """
        SELECT id, full_name, age, position, wealth
        FROM people
        ORDER BY id ASC
    """
    columns, results = execute_query(query)
    return render_template(
        "results.html",
        results=results,
        message=None,
        search_term="",
        total_billionaires=0,
        percentage=0,
        total_billionaires_in_database=0,
    )

@app.route("/search_by_country", methods=["POST"])
def search_by_country():
    country_name = request.form.get("country_name", "").strip()

    if not country_name:
        return render_template(
            "results.html",
            results=[],
            message="Por favor, insira um país para pesquisa.",
            search_term=country_name,
            total_billionaires=0,
            percentage=0,
            total_billionaires_in_database=0,
        )

    query = """
        SELECT p.id, p.full_name, p.age, p.position, p.wealth, c.id AS country_id
        FROM people p
        JOIN residences r ON p.residence_id = r.id
        JOIN countries c ON r.country_id = c.id
        WHERE r.country_of_residence LIKE ?
        ORDER BY p.id ASC
    """
    params = [f"%{country_name}%"]
    columns, results = execute_query(query, params)

    total_billionaires = len(results)

    query_total = "SELECT COUNT(*) FROM people"
    columns_total, total_results = execute_query(query_total)
    total_billionaires_in_database = total_results[0][0]

    percentage = (total_billionaires / total_billionaires_in_database) * 100 if total_billionaires_in_database else 0

    return render_template(
        "results.html",
        results=results,
        message=None if results else "Nenhum bilionário encontrado para este país.",
        search_term=country_name,
        total_billionaires=total_billionaires,
        percentage=percentage,
        total_billionaires_in_database=total_billionaires_in_database,
    )

@app.route("/billionaire/<int:person_id>")
def billionaire_details(person_id):
    query = """
        SELECT p.full_name, p.position, p.birth_date, p.gender, p.wealth, 
               p.age, i.industry, i.source, p.citizenship, r.country_of_residence,
               r.city_of_residence, r.residence_state, r.residence_region, r.country_id
        FROM people p
        JOIN industries i ON p.industry_id = i.id
        JOIN residences r ON p.residence_id = r.id
        WHERE p.id = ?
    """
    params = [person_id]
    columns, results = execute_query(query, params)
    if results:
        details = results[0]
        return render_template("billionaire_details.html", details=details, full_name=details[0])
    else:
        return render_template("billionaire_details.html", message="Bilionário não encontrado.")

@app.route("/all")
def all_billionaires():
    query = """
        SELECT id, full_name, age, position, wealth
        FROM people
        ORDER BY full_name ASC
    """
    columns, results = execute_query(query)
    return render_template(
        "results.html",
        results=results,
        message=None,
        search_term="",
        total_billionaires=0,
        percentage=0,
        total_billionaires_in_database=0,
    )

@app.route("/country/<int:country_id>")
def country_details(country_id):
    query = """
        SELECT con.continent, c.country_pop, c.country_lat, c.country_long, 
               c.cpi_country, c.cpi_change_country, c.gdp_country, 
               c.g_tertiary_ed_enroll, c.g_primary_ed_enroll, c.life_expectancy, c.tax_revenue, 
               c.tax_rate, r.country_of_residence
        FROM countries c
        JOIN continents con on con.id = c.continent_id
        JOIN residences r ON r.country_id = c.id 
        WHERE c.id = ?
    """
    params = [country_id]
    columns, results = execute_query(query, params)
    if results:
        country_details = results[0]
        country_name = country_details[12]  # Nome do país
        return render_template("country_details.html", country_details=country_details, country_name=country_name)
    else:
        return render_template("country_details.html", message="Detalhes do país não encontrados.")


@app.route('/countries_by_billionaires')
def countries_by_billionaires():
    countries_query = """
    SELECT r.country_id, 
           r.country_of_residence AS country_name, 
           COUNT(p.id) AS num_billionaires,
           p.id AS billionaire_id,  
           (SELECT p2.full_name
            FROM people p2
            JOIN residences r2 ON p2.residence_id = r2.id
            WHERE r2.country_of_residence = r.country_of_residence
            ORDER BY p2.wealth DESC
            LIMIT 1) AS richest_billionaire_name,  
           (SELECT i.industry
            FROM people p3
            JOIN industries i ON p3.industry_id = i.id
            JOIN residences r3 ON p3.residence_id = r3.id
            WHERE r3.country_of_residence = r.country_of_residence
            GROUP BY i.industry
            ORDER BY COUNT(p3.id) DESC
            LIMIT 1) AS top_industry
    FROM residences r
    JOIN people p ON r.id = p.residence_id
    GROUP BY r.country_of_residence, r.country_id
    ORDER BY num_billionaires DESC;

    """
    _, countries = execute_query(countries_query)

    return render_template('countries_by_billionaires.html', countries=countries)

@app.route('/industries_by_wealth')
def industries_by_wealth():
    # Consulta SQL atualizada para exibir apenas os nomes das indústrias ordenados por soma de riqueza
    industries_query = """
    SELECT i.id, i.industry AS Industry, SUM(p.wealth) AS total_wealth
    FROM industries i 
    JOIN people p ON i.id = p.industry_id
    GROUP BY i.industry
    ORDER BY total_wealth DESC;
    """
    _, industries = execute_query(industries_query)
    return render_template('industries.html', industries=industries)


@app.route('/industry_details/<string:industry_name>')
def industry_details(industry_name):
    # Consulta SQL para obter os detalhes da indústria
    industry_details_query = """
    SELECT p.id, p.full_name, p.age, p.wealth, i.source
    FROM industries i
    JOIN people p ON i.id = p.industry_id
    WHERE i.industry=?
    ORDER BY wealth DESC
    LIMIT 5
    """

    country_and_continent_query = """
    SELECT r.country_of_residence AS country_name, ct.continent
    FROM industries i
    JOIN people p ON i.id = p.industry_id
    JOIN residences r ON p.residence_id = r.id
    JOIN countries c ON r.country_id = c.id
    JOIN continents ct ON c.continent_id = ct.id
    WHERE i.industry = ?
    GROUP BY r.country_of_residence, ct.continent
    ORDER BY COUNT(p.id) DESC
    LIMIT 1;
    """

    _, top_billionaires = execute_query(industry_details_query, (industry_name,))
    _, country_and_continent = execute_query(country_and_continent_query, (industry_name,))

    if top_billionaires and country_and_continent:
        industry_name = industry_name
        source = top_billionaires[0][4]
        country = country_and_continent[0][0]
        continent = country_and_continent[0][1]
    else:
        source = country = continent = "N/A"

    return render_template('industry_details.html',
                           industry_name=industry_name,
                           top_billionaires=top_billionaires,
                           source=source,
                           country=country,
                           continent=continent)


@app.route('/industry_all/<string:industry_name>')
def industry_all(industry_name):
    all_billionaires_query = """
    SELECT p.id, p.full_name,p.age, p.wealth, i.source
    FROM industries i
    JOIN people p ON i.id = p.industry_id
    WHERE i.industry = ?
    ORDER BY wealth DESC
    """
    _, all_billionaires = execute_query(all_billionaires_query, (industry_name,))

    return render_template(
        'industry_all.html',
        industry_name=industry_name,
        all_billionaires=all_billionaires
    )


@app.route("/gender_stats")
def gender_stats():
    gender_query = """
        SELECT 
            p.gender,
            COUNT(*) AS total,
            ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM people)), 2) AS percentage,
            
            (SELECT i.industry
             FROM industries i
             JOIN people p2 ON p2.industry_id = i.id
             WHERE p2.gender = p.gender
             GROUP BY i.industry
             ORDER BY COUNT(*) DESC LIMIT 1) AS industry,
             
            (SELECT r.country_of_residence
             FROM residences r
             JOIN people p2 ON p2.residence_id = r.id
             WHERE p2.gender = p.gender
             GROUP BY r.country_of_residence
             ORDER BY COUNT(*) DESC LIMIT 1) AS country,
             
            (SELECT con.continent
             FROM countries c
             JOIN residences r ON r.country_id = c.id
             JOIN continents con ON c.continent_id = con.id
             JOIN people p2 ON p2.residence_id = r.id
             WHERE p2.gender = p.gender
             GROUP BY con.continent
             ORDER BY COUNT(*) DESC LIMIT 1) AS continent,
            ROUND(AVG(p.wealth), 2) AS average_wealth
        FROM people p
        GROUP BY p.gender
    """
    _, gender_info = execute_query(gender_query)


    men_info_query = """
        SELECT i.industry, c.cpi_country, con.continent,
            COUNT(*) AS count
        FROM people p
        JOIN industries i ON p.industry_id = i.id
        JOIN residences r ON p.residence_id = r.id
        JOIN countries c ON r.country_id = c.id
        JOIN continents con ON c.continent_id = con.id
        WHERE p.gender = 'M'
        GROUP BY i.industry, c.cpi_country, con.continent
        ORDER BY count DESC
        LIMIT 1
    """
    _, men_info = execute_query(men_info_query)


    women_info_query = """
        SELECT i.industry, c.cpi_country, con.continent,
            COUNT(*) AS count
        FROM people p
        JOIN industries i ON p.industry_id = i.id
        JOIN residences r ON p.residence_id = r.id
        JOIN countries c ON r.country_id = c.id
        JOIN continents con ON c.continent_id = con.id
        WHERE p.gender = 'F'
        GROUP BY i.industry, c.cpi_country, con.continent
        ORDER BY count DESC
        LIMIT 1
    """
    _, women_info = execute_query(women_info_query)


    top_men_query = """
        SELECT p.id, p.full_name, p.age, p.position, p.wealth, i.industry
        FROM people p
        JOIN industries i ON p.industry_id = i.id
        WHERE p.gender = 'M'
        ORDER BY p.wealth DESC
        LIMIT 3
    """
    _, top_men = execute_query(top_men_query)


    top_women_query = """
        SELECT p.id, p.full_name, p.age, p.position, p.wealth, i.industry
        FROM people p
        JOIN industries i ON p.industry_id = i.id
        WHERE p.gender = 'F'
        ORDER BY p.wealth DESC
        LIMIT 3
    """
    _, top_women = execute_query(top_women_query)

    return render_template(
        "gender_stats.html",
        gender_info=gender_info,
        men_info=men_info[0],
        women_info=women_info[0],
        top_men=top_men,
        top_women=top_women
    )


@app.route("/us_non_tech_billionaires")
def us_non_tech_billionaires():
    query = """
    SELECT DISTINCT
        p.id AS billionaire_id,
        p.full_name AS full_name, 
        i.industry AS industry 
    FROM 
        people p
    JOIN 
        industries i ON p.industry_id = i.id
    WHERE 
        i.industry NOT IN (
            SELECT DISTINCT industry
            FROM industries
            WHERE industry LIKE 'Technology'
        )
    AND p.citizenship LIKE 'United States'
    ORDER BY p.full_name;
    """
    columns, results = execute_query(query)
    return render_template("us_non_tech_billionaires.html", results=results, columns=columns)


@app.route("/us_cities_with_billionaires")
def us_cities_with_billionaires():
    query = """
    SELECT r.city_of_residence, COUNT(p.id) AS people_count
    FROM Residences r
    JOIN People p ON r.id = p.residence_id
    WHERE r.country_of_residence = 'United States'
    GROUP BY r.city_of_residence
    HAVING COUNT(p.id) >= 2
    ORDER BY people_count DESC;
    """
    columns, results = execute_query(query)
    return render_template("us_cities_with_billionaires.html", results=results, columns=columns)


