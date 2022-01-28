import datetime

import sqlalchemy
from mongoengine import Document,StringField,IntField,ListField,DateField,ObjectIdField
from bson import ObjectId
from sqlalchemy import Date


class Employers(Document):
    _id = ObjectId()
    name=StringField()
    email = StringField()
    designation=StringField()
    company_name=StringField()
    contact=StringField()
    address=StringField()
    hashed_password = StringField()
    status =IntField()
    def _init__(self, name, email,hashed_password,designation,company_name,contact,address,status,id):
        self.name = name
        self.email= email
        self.hashed_password=hashed_password
        self.designation=designation
        self.company_name=company_name
        self.contact=contact
        self.address=address
        self.status=status
        self._id=id

class Candidates(Document):

    _id = ObjectId()
    name = StringField()
    email = StringField()
    hashed_password = StringField()
    dob=StringField()
    contact = StringField()
    address = StringField()
    grad = StringField()
    post_grad=StringField()
    resume=StringField()
    skills=ListField()
    status = IntField()
    def _init__(self, name, email,hashed_password,dob,contact,address,grad,post_grad,resume,skills,status,id):
        self.name = name
        self.email= email
        self.hashed_password=hashed_password
        self.dob=dob
        self.contact=contact
        self.address=address
        self.grad =grad
        self.post_grad = post_grad
        self.resume = resume
        self.skills = skills
        self.status=status
        self._id=id

class Jobs(Document):

    _id=ObjectId()
    title=StringField()
    post=StringField()
    description=StringField()
    company_name=StringField()
    annual_salary_in_lakhs=StringField()
    job_location=StringField()
    apply_from=DateField()
    apply_to=DateField()
    status=IntField()
    posted_by=StringField()
    def _init__(self,id, title,post,description,company_name,annual_salary_in_lakhs,job_location,apply_from,apply_to,posted_by,status):
        self._id = id
        self.title = title
        self.post=post
        self.description= description
        self.company_name=company_name
        self.annual_salary_in_lakhs=annual_salary_in_lakhs
        self.job_location=job_location
        self.apply_from=apply_from
        self.apply_to =apply_to
        self.posted_by = posted_by
        self.status=status

class Apply(Document):

    _id=IntField(primary_key=True,index=True)
    job_id=StringField()
    cand_id=StringField()
    apply_date=StringField()
    def _init__(self, job_id,cand_id,apply_date,id):
        self.job_id = job_id
        self.cand_id=cand_id
        self.apply_date= apply_date
        self._id=id

class Admin(Document):

    _id=ObjectId()
    username=StringField()
    password=StringField()

class Interview(Document):

    _id=IntField(primary_key=True,index=True)
    job_id=StringField()
    cand_id = StringField()
    emp_id = StringField()
    venue=StringField()
    day=StringField()
    time=StringField()
    message=StringField()
    def _init__(self, job_id,cand_id,emp_id,venue,day,time,message,id):
        self.job_id = job_id
        self.cand_id=cand_id
        self.emp_id=emp_id
        self.venue=venue
        self.day=day
        self.time=time
        self.message=message
        self._id=id
