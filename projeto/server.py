import warnings
from app import app  # Importa o app criado no `app.py`

warnings.filterwarnings('ignore', category=FutureWarning)

if __name__ == "__main__":
    app.run(debug=True)
