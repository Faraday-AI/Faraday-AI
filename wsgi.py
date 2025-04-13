import os
from app.main import app

# This is required for WSGI
application = app 

if __name__ == "__main__":
    app.run() 