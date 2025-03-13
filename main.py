from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
# ... (keep your existing imports)

app = FastAPI()

# Add this new root route at the top of your routes
@app.get("/")
async def root():
    """Root endpoint that returns a simple HTML page"""
    html_content = """
    <html>
        <head>
            <title>Faraday AI</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <h1>Welcome to Faraday AI</h1>
            <p>Coming Soon</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# ... (rest of your existing code)
