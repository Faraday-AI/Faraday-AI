import os
from app.main import app

# This is required for WSGI
application = app 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 