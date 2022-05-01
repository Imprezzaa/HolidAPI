from fastapi import FastAPI
from requests import get
from datetime import datetime
from pydantic import BaseModel
from collections import defaultdict


# https://fastapi.tiangolo.com/tutorial/body/#results
# class defines requirements for the incoming data
class DateReq(BaseModel):
    dates: list[str]
    # will be automagically added to API documentation

    class Config:
        schema_extra = {"dates": ["2022-01-02"]}

# class defines the response body
class Dates_Resp(BaseModel):
    resp_message: str = "There are no holidays on this date."
    holidays: list = [] 
    # will be automagically added to API documentation

    class Config:
        schema_extra = {
            "message": "2022-02-21 is a holiday!",
            "holidays": [{
                "date": "2022-02-21",
                "localName": "Presidents Day",
                "name": "Washington's Birthday",
                "countryCode": "US",
                "fixed": "false",
                "global": "true",
                "counties": "null",
                "launchYear": "null",
                "types": [
                    "Public"
                ]
            }]
        }

# couple of loose variables to grab our current year and create a default dict to store data in
year = str(datetime.now().year)
holidata = defaultdict(list) 

# TODO - allow requests to set a country code and year manually
def get_holidata(year: str = year):
    '''defaults to US in $current_year
    # using the nager.Nager docker image to pull info
    # https://date.nager.at/api/v3/PublicHolidays/2022/US
    '''
    r = get(f"http://localhost:5001/api/v3/PublicHolidays/{year}/US")

    return r.json()

# 
def build_holidata():
    '''
    takes output of get_holidata and saves it into holidata to be accessed by other functions
    '''
    holidata_json = get_holidata()
    for item in holidata_json:
        holidata[item["date"]].append(item)

"""
just kicks off data building when file is run, not great, can do better
TODO: find a better way to store pulled data - maybe a CountryCode class or something
"""
build_holidata()


app = FastAPI()

# root endpoint, returns a short message
@app.get("/")
async def root():
    return {"Welcome to HolidayPI v.01!"}

# endpoint returns the holidata dictionary in all it's glory
@app.get("/holidays")
def get_list():
    return holidata

# endpoint that will take in json formatted data in a form outlined in the DataReq class
@app.get("/holidays/date")
def get_date(datareq: DateReq):
    resp = Dates_Resp()
    c = 0
    dates = datareq.dates
    for item in dates:
        if item in holidata:
            resp.holidays = resp.holidays + holidata.get(item)
            c += 1
    if c > 1:
        resp.resp_message = "There are holidays on these dates!"
    elif c == 1:
        resp.resp_message = "There is a holiday on this date!"
    return resp
