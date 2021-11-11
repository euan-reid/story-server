"""
It'll do stuff (later)
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(default_response_class=HTMLResponse)

@app.get('/')
async def home():
    """
    Shows the homepage
    """
    return '''
    <!DOCTYPE html>
    <html>
        <head>
            <title>Page!</title>
        </head>
        <body>
            <p>Test!</p>
        </body>
    </html>
    '''
