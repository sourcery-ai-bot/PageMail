# Imports
import logging
import os
import sys
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
load_dotenv()

# Logging on
logging.basicConfig()
app_log = logging.getLogger("Application Log")
# Change in production
logging.getLogger('uvicorn').setLevel(logging.ERROR)
logging.getLogger('apscheduler').setLevel(logging.INFO)

# Get the database connection and models
from API.db.connection import database

# Get the task scheduler and start it on app launch
from API.helpers.scheduling import scheduler

# Get the jobs which are to be scheduled on startup
from API.helpers.utils import update_metadata

# Get the routers
from API.routes.pages import router as pages_router
from API.routes.users import router as users_router

# Define app and include routers and connection events.
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(users_router)
app.include_router(pages_router)

# Events
@app.on_event('startup')
async def on_startup():
    scheduler.start()
    try:
        metadata_job = scheduler.add_job(update_metadata, 'interval', minutes=1, id="1")
    except:
        print("metadata job already exists")
    await database.connect()

@app.on_event('shutdown')
async def on_shutdown():
    scheduler.shutdown()
    await database.disconnect()

@app.get('/')
async def welcome():
    return "Hello World."

# UPDATE: Change user info

# GET: Get all pages for a user
# UPDATE: User preferences
# DELETE: Delete a post for a user