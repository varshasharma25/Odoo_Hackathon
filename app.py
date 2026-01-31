import os
from app import create_app

# Use standard ASCII character to avoid Windows encoding issues
print("ENV CHECK - DB_NAME:", os.getenv("DB_NAME"))

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
