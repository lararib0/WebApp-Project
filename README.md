# Web App  
Assignment for Databases, 2º Year, 1º Semester  

---

## Summary  
This project aims to develop a web application displaying information about billionaires worldwide. It involves designing a relational database, importing data from a CSV file, and creating a Flask-based web interface for users to query and visualize data.



## Tools and Technologies Used  
- **Database**: SQLite  
- **Web Framework**: Flask  
- **Programming Language**: Python  
- **Frontend**: HTML, CSS, Jinja Templates  
- **Libraries**: pandas, sqlite3  




## Requirements  
To install the required dependencies, run:

```bash
pip3 install -r requirements.txt
```



## How to Run the Application  

1. **Install dependencies**:

    ```bash
    pip3 install -r requirements.txt
    ```

2. **Import data into the database**:

    ```bash
    python3 test.py
    ```

3. **Run the Flask server**:

    ```bash
    python3 server.py
    ```

4. **Visit** [http://127.0.0.1:5000](http://127.0.0.1:5000) **to view the app**.




## File Structure

- `utils.py`: Functions for database setup and data import.  
- `test.py`: Imports CSV data into the database.  
- `app.py`: Defines Flask routes and logic.  
- `server.py`: Starts the Flask server.  
- `data/`: Contains CSV and database files.  
- `templates/`: HTML templates for rendering pages.






## Authors  
- **Lara Ribeiro**  
- **Benedita Marques**  
- **Mariana Pinho**  
- **Eduardo Oliveira**



