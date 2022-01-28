from pymongo import MongoClient
conn=MongoClient("mongodb://localhost:27017/")
db=conn["job_portal"]
employers=db["employers"]
candidates=db["candidates"]
