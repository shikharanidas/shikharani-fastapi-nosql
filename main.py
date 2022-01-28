from typing import List
import datetime
import re
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import FileResponse
from fastapi import Depends, FastAPI, HTTPException,status,UploadFile,File,Query
from sqlalchemy.orm import Session
import crud, models, schemas
from database import employers,candidates
from datetime import datetime,date
import secrets
from passlib.context import CryptContext
from models import Employers,Candidates,Jobs,Admin,Apply,Interview
from mongoengine import connect
import json,pymongo
import schemas
from mongoengine import DateField
from bson import ObjectId

description = """
_Online Job Portal helps to connect employers with candidates in order to meet their requirements and goals._

## Employers

They can:

* **Create account**.
* **View profile**.
* **Update profile**.
* **Post jobs**.
* **Get posted jobs list**.
* **Get candidates list for particular job**.
* **Download candidates resume**.
* **Schedule Interview**.
* **View all interview schedules**.
* **Search candidates by skills**.

## Candidates

They can:

* **Create account**.
* **View profile**.
* **Update profile**.
* **View jobs**.
* **Search jobs**.
* **Apply for jobs and upload resume**.
* **View/Download resume**.
* **Update their resume**.
* **Get list of applied jobs**.
* **View interview schedules**.

## Admin

Admin can:

* **View all employers**.
* **Search employer by id**.
* **Delete employer**.
* **View all candidates**.
* **Search candidate by id**.
* **Delete candidate**.
* **View jobs**.
* **Delete job**.
* **View interview schedules**.

"""

# models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="Online Job Portal",description=description)
conn=connect(db="job_portal",host="localhost",port=27017)
security=HTTPBasic()
db=conn['job_portal']
emp_coll=db['employers']

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_current_employer(credentials: HTTPBasicCredentials = Depends(security)):
    db_employer = json.loads(Employers.objects(email=credentials.username).to_json())
    if db_employer==[]:
        raise HTTPException(status_code=401,detail="Invalid User!!")

    for employers in Employers.objects:
        if employers.email==credentials.username:
            if not verify_password(credentials.password,employers.hashed_password):
                raise HTTPException(status_code=401,detail="Incorrect Username or password!!")

    return db_employer

def get_current_candidate(credentials: HTTPBasicCredentials = Depends(security)):
    db_candidate = json.loads(Candidates.objects(email=credentials.username).to_json())
    if db_candidate == []:
        raise HTTPException(status_code=401, detail="Invalid User!!")

    for candidates in Candidates.objects:
        if candidates.email == credentials.username:
            if not verify_password(credentials.password, candidates.hashed_password):
                raise HTTPException(status_code=401, detail="Incorrect Username or password!!")

    return db_candidate

def get_admin(credentials: HTTPBasicCredentials = Depends(security)):
    db_admin=json.loads(Admin.objects(username=credentials.username,password=credentials.password).to_json())
    if db_admin!=[]:
        return True
    if db_admin ==[]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid user!!")
    return db_admin

# welcome to job portal

@app.get("/welcome/",tags=["welcome"],responses={200: {
            "content": {"image/png": {}},
            "description": "Return an image.",
        }
    },)
def welcome_to_job_portal():
    return FileResponse("images/OnlineJobPortal.png",media_type="image/png")

# employers


@app.post("/employers/create/", response_model=schemas.Employer,tags=["employers"],status_code=201,responses={201: {
            "content": {"image/png": {}},
            "description": "Return an image.",
        }
    },)
def create_employer(employer: schemas.EmployerCreate):
    db_employer = json.loads(Employers.objects(email=employer.email).to_json())
    if db_employer!=[]:
        raise HTTPException(status_code=409, detail="Email already registered")
    if employer.name=="" or employer.contact=="" or employer.designation=="" or employer.email=="" or employer.address==""\
            or employer.company_name=="" or employer.password=="":
        raise HTTPException(status_code=422,detail="Fields can't be empty!!")
    if (bool(re.match('^[a-zA-Z. ]*$', employer.name)) == False):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid value for name!!")
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(email_pattern, employer.email)):
        raise HTTPException(status_code=422, detail="Invalid Email format!!")
    if (bool(re.match('^[a-zA-Z. ]*$', employer.company_name)) == False):
        raise HTTPException(status_code=422, detail="Invalid value for company_name!!")
    if (bool(re.match('^[a-zA-Z. ]*$', employer.designation)) == False):
        raise HTTPException(status_code=422, detail="Invalid value for designation!!")
    x = re.findall("\D", employer.contact)
    if x:
        raise HTTPException(status_code=422, detail="Enter only digits!!")
    if len(employer.contact) < 10 or len(employer.contact) > 10:
        raise HTTPException(status_code=422, detail="Contact should be of 10 digits!!")
    if len(employer.password)<8:
        raise HTTPException(status_code=422,detail="Password should be of minimum 8 characters!!")
    # id=employers.insert_one(dict(employer))
    hash_pwd=get_password_hash(employer.password)
    e1 = Employers(name=employer.name, email=employer.email,hashed_password=hash_pwd, designation=employer.designation,
                   company_name=employer.company_name,contact=employer.contact,address=employer.address,status=1)
    e1.save()
    return FileResponse("images/welcome.png", media_type="image/png",status_code=201)

@app.get("/employers/welcome_employers/",tags=["employers"],responses={200: {
            "content": {"image/gif": {}},
            "description": "Return an image.",
        }
    },dependencies=[Depends(get_current_employer)])
def welcome_employers():
    return FileResponse("images/emp1.gif",media_type="image/gif")

@app.get("/employers/me/",tags=["employers"],status_code=200)
def view_your_profile(current_employer:schemas.Employer= Depends(get_current_employer)):
    return {"_id":current_employer[0]["_id"]["$oid"],
            "name":current_employer[0]["name"],
            "email":current_employer[0]["email"],
            "designation": current_employer[0]["designation"],
    "company_name": current_employer[0]["company_name"],
    "contact": current_employer[0]["contact"],
    "address":current_employer[0]["address"]}

@app.put("/employers/update",dependencies=[Depends(get_current_employer)],status_code=200,tags=["employers"])
def update_profile(employer:schemas.EmployerUpdate,emp_update:schemas.Employer=Depends(get_current_employer)):
    id = emp_update[0]["_id"]["$oid"]
    emp_id = ObjectId(id)
    db_employer=json.loads(Employers.objects(id=emp_id).to_json())
    if db_employer ==[]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Employer with id:{emp_id} does not exist!!")

    if employer.name!=None:
        if employer.name =="":
            raise HTTPException(status_code=422, detail="Fields can't be empty!!")
        if (bool(re.match('^[a-zA-Z. ]*$', employer.name)) == False):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid value for name!!")
        Employers.objects(id=emp_id).update_one(name=employer.name)
    if employer.designation!=None:
        if employer.designation == "":
            raise HTTPException(status_code=422, detail="Fields can't be empty!!")
        if (bool(re.match('^[a-zA-Z. ]*$', employer.designation)) == False):
            raise HTTPException(status_code=422, detail="Invalid value for designation!!")
        Employers.objects(id=emp_id).update_one(designation=employer.designation)
    if employer.company_name!=None:
        if employer.company_name == "":
            raise HTTPException(status_code=422, detail="Fields can't be empty!!")
        if (bool(re.match('^[a-zA-Z. ]*$', employer.company_name)) == False):
            raise HTTPException(status_code=422, detail="Invalid value for company_name!!")
        Employers.objects(id=emp_id).update_one(company_name=employer.company_name)
    if employer.contact!=None:
        if employer.contact == "":
            raise HTTPException(status_code=422, detail="Fields can't be empty!!")
        x = re.findall("\D", employer.contact)
        if x:
            raise HTTPException(status_code=422, detail="Enter only digits!!")
        if len(employer.contact) < 10 or len(employer.contact) > 10:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail="Contact should be of 10 digits!!")
        Employers.objects(id=emp_id).update_one(contact=employer.contact)
    if employer.address!=None:
        if employer.address == "":
            raise HTTPException(status_code=422, detail="Fields can't be empty!!")
        Employers.objects(id=emp_id).update_one(address=employer.address)

    return {"message":"Successfully Updated!!"}

@app.get("/employers/jobs/",dependencies=[Depends(get_current_employer)],tags=["employers"])
def get_posted_jobs(employer:schemas.Employer=Depends(get_current_employer)):
    id = employer[0]["_id"]["$oid"]
    emp_id = id
    db_jobs=json.loads(Jobs.objects(posted_by=emp_id).to_json())
    if db_jobs ==[]:
        raise HTTPException(status_code=400,detail="No jobs posted!!")
    return db_jobs

@app.get("/employers/{job_id}",dependencies=[Depends(get_current_employer)],tags=["employers"])
def view_candidates(job_id:str,employer: schemas.Employer = Depends(get_current_employer)):
    emp_id = employer[0]["_id"]["$oid"]
    # emp_id = ObjectId(id)
    db_job = json.loads(Jobs.objects(id=job_id).to_json())
    if db_job ==[]:
        raise HTTPException(status_code=404, detail=f"Job with id: {job_id} does not exist!!")
    check_job = json.loads(Jobs.objects(id=job_id,posted_by=emp_id).to_json())
    if check_job ==[]:
        raise HTTPException(status_code=400, detail="This job is not posted by you!!You can view applied candidates "
                                                    "only for jobs posted by you!!")
    db_apply=json.loads(Apply.objects(job_id=job_id).to_json())
    if db_apply==[]:
        raise HTTPException(status_code=404,detail="No Candidates found!!")
    return db_apply

@app.post("/employers/interview/",tags=["employers"],status_code=201,
          dependencies=[Depends(get_current_employer)])
def schedule_interview(job_id:str,cand_id:str,interview: schemas.InterviewCreate,
                       employer: schemas.Employer = Depends(get_current_employer)):
    emp_id = employer[0]["_id"]["$oid"]
    # emp_id = ObjectId(id)
    db_job = json.loads(Jobs.objects(id=job_id).to_json())
    if db_job == []:
        raise HTTPException(status_code=404, detail=f"Job with id: {job_id} does not exist!!")
    check_job=json.loads(Jobs.objects(id=job_id,posted_by=emp_id).to_json())
    if check_job==[]:
        raise HTTPException(status_code=400,detail="This job is not posted by you!!You can schedule interview "
                                                   "only for jobs posted by you!!")
    db_cand=json.loads(Candidates.objects(id=cand_id).to_json())
    if db_cand ==[]:
        raise HTTPException(status_code=404,detail=f"Candidate with id: {cand_id} does not exist!!")
    check_apply_job=json.loads(Apply.objects(cand_id=cand_id,job_id=job_id).to_json())
    if check_apply_job ==[]:
        raise HTTPException(status_code=400,detail="This candidate has not applied for this job!!")
    db_interview_schedule=json.loads(Interview.objects(job_id=job_id,cand_id=cand_id).to_json())
    if db_interview_schedule:
        raise HTTPException(status_code=409,detail="You have already scheduled an interview for this candidate!!")
    if interview.venue=="" or interview.day=="" or interview.time=="" or interview.message=="":
        raise HTTPException(status_code=422,detail="Fields can't be empty!!")
    if (bool(re.match(
            '^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$',
            interview.day)) == False):
        raise HTTPException(status_code=422, detail="Invalid date format!!Correct format is yyyy-mm-dd!!")
    time_re = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$')

    if bool(time_re.match(interview.time))==False:
        raise HTTPException(status_code=422,detail="Invalid time format!!Correct time format is from 00:00 to 24:00")
    ct=Interview.objects().count()
    i_id=ct+1
    i1=Interview(venue=interview.venue,day=interview.day,time=interview.time,message=interview.message,job_id=job_id,cand_id=cand_id,
              emp_id=emp_id,id=i_id)
    i1.save()
    return {"message":"Interview Scheduled!!"}

@app.get("/employers/interview-schedules/",tags=["employers"],dependencies=[Depends(get_current_employer)])
def view_all_interview_schedules(employer:schemas.Employer=Depends(get_current_employer)):
    emp_id = employer[0]["_id"]["$oid"]
    # emp_id = ObjectId(id)
    db_interview=json.loads(Interview.objects(emp_id=emp_id).to_json())
    if db_interview==[]:
        raise HTTPException(status_code=404,detail="No interview scheduled yet!!")
    return db_interview

@app.get("/employers/{skills}/",dependencies=[Depends(get_current_employer)],tags=["employers"])
def search_candidates_by_skills(skills:str):
    db_cand = json.loads(Candidates.objects(skills=skills).to_json())
    if (bool(re.match('^[a-zA-Z#+]*$', skills)) == False):
        raise HTTPException(status_code=422, detail="Enter valid skills!!")
    if db_cand == []:
        raise HTTPException(status_code=404, detail="No candidates found having this skill!!")

    return db_cand

@app.post("/employers/download-resume/",dependencies=[Depends(get_current_employer)],tags=["employers"])
def download_candidate_resume(cand_id:str):

    db_cand = json.loads(Candidates.objects(id=cand_id).to_json())
    if db_cand == []:
        raise HTTPException(status_code=400, detail="Candidate with id:{cand_id} does not exist!!!!")
    resume=db_cand[0]["resume"]
    if resume=="":
        raise HTTPException(status_code=400,detail="This candidate has not uploaded resume!!")

    return FileResponse(f'files/{resume}',media_type="application/pdf",filename=resume)

# candidates


@app.post("/candidates/create/", response_model=schemas.Candidate,tags=["candidates"],status_code=201,responses={201: {
            "content": {"image/png": {}},
            "description": "Return an image.",
        }
    },)
def create_candidate(candidate: schemas.CandidateCreate,skills:List[str]=Query(...)):
    db_candidate = json.loads(Candidates.objects(email=candidate.email).to_json())
    if db_candidate:
        raise HTTPException(status_code=409, detail="Email already registered")
    if candidate.name=="" or candidate.contact=="" or candidate.dob=="" or candidate.email=="" or candidate.address==""\
            or candidate.grad=="" or candidate.post_grad=="" or candidate.password=="" :
        raise HTTPException(status_code=422,detail="Fields can't be empty!!")
    if (bool(re.match('^[a-zA-Z. ]*$', candidate.name)) == False):
        raise HTTPException(status_code=422, detail="Invalid value for name!!")
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not (re.fullmatch(email_pattern, candidate.email)):
        raise HTTPException(status_code=422, detail="Invalid Email format!!")
    if (bool(re.match('^[a-zA-Z. ]*$', candidate.grad)) == False):
        raise HTTPException(status_code=422, detail="Invalid value for grad!!")
    if (bool(re.match('^[a-zA-Z. ]*$', candidate.post_grad)) == False):
        raise HTTPException(status_code=422, detail="Invalid value for post_grad!!")
    # if (bool(re.match('^[a-zA-Z]*$',i for i in candidate.skills)) == False):
    #     raise HTTPException(status_code=422, detail="Invalid value for skills!!")
    if (bool(re.match(
            '^([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$',
            candidate.dob)) == False):
        raise HTTPException(status_code=422, detail="Invalid dob format!!Correct format is yyyy-mm-dd!!")
    x = re.findall("\D", candidate.contact)
    if x:
        raise HTTPException(status_code=422, detail="Enter only digits!!")
    if len(candidate.contact) < 10 or len(candidate.contact) > 10:
        raise HTTPException(status_code=422, detail="Contact should be of 10 digits!!")
    if len(candidate.password)<8:
        raise HTTPException(status_code=422,detail="Password should be of minimum 8 characters!!")
    resume=""
    # if skills[0]=="string" or skills[1]=="string" or skills[2]=="string" or skills[3]=="string":
    #     raise HTTPException(status_code=422,detail="Enter valid skills!!")
    hash_pwd = get_password_hash(candidate.password)
    c1 = Candidates(name=candidate.name, email=candidate.email, hashed_password=hash_pwd, dob=candidate.dob,
                    contact=candidate.contact, address=candidate.address,grad=candidate.grad,post_grad=candidate.post_grad,
                    resume=resume,skills=skills, status=1)
    c1.save()

    return FileResponse("images/wel2.png", media_type="image/png",status_code=201)

@app.get("/welcome_candidates/",tags=["candidates"],responses={200: {
            "content": {"image/gif": {}},
            "description": "Return an image.",
        }
    },dependencies=[Depends(get_current_candidate)])
def welcome_candidates():
    return FileResponse("images/cand5.gif",media_type="image/gif")

@app.get("/candidates/me/",tags=["candidates"],status_code=200,dependencies=[Depends(get_current_candidate)])
def view_your_profile(current_candidate: schemas.Candidate = Depends(get_current_candidate)):
    return {"_id":current_candidate[0]["_id"]["$oid"],
            "name":current_candidate[0]["name"],
            "email":current_candidate[0]["email"],
            "dob": current_candidate[0]["dob"],
    "contact": current_candidate[0]["contact"],
            "address":current_candidate[0]["address"],
    "grad":current_candidate[0]["grad"],
            "post_grad":current_candidate[0]["post_grad"],
            "skills":current_candidate[0]["skills"],
            "resume":current_candidate[0]["resume"]}

@app.put("/candidates/update",dependencies=[Depends(get_current_candidate)],status_code=200,tags=["candidates"])
def update_profile(candidate:schemas.CandidateUpdate,skills:List[str]=Query(None),cand_update:schemas.Candidate=Depends(get_current_candidate)):
    id = cand_update[0]["_id"]["$oid"]
    cand_id = ObjectId(id)
    db_candidate=json.loads(Candidates.objects(id=cand_id).to_json())
    if db_candidate ==[]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Candidate with id:{cand_id} does not exist!!")

    if candidate.name!=None:
        if candidate.name == "":
            raise HTTPException(status_code=422, detail="Fields can't be empty!!")
        if (bool(re.match('^[a-zA-Z. ]*$', candidate.name)) == False):
            raise HTTPException(status_code=422, detail="Invalid value for name!!")
        Candidates.objects(id=cand_id).update_one(name=candidate.name)

    if candidate.grad!=None:
        if candidate.grad == "":
            raise HTTPException(status_code=422, detail="Fields can't be empty!!")
        if (bool(re.match('^[a-zA-Z. ]*$', candidate.grad)) == False):
            raise HTTPException(status_code=422, detail="Invalid value for grad!!")
        Candidates.objects(id=cand_id).update_one(grad=candidate.grad)
    if candidate.post_grad != None:
        if candidate.post_grad == "":
            raise HTTPException(status_code=422, detail="Fields can't be empty!!")
        if (bool(re.match('^[a-zA-Z. ]*$', candidate.post_grad)) == False):
            raise HTTPException(status_code=422, detail="Invalid value for post_grad!!")
        Candidates.objects(id=cand_id).update_one(post_grad=candidate.post_grad)

    if skills!=None:
        Candidates.objects(id=cand_id).update_one(skills=skills)
    if candidate.contact!=None:
        if candidate.contact == "":
            raise HTTPException(status_code=422, detail="Fields can't be empty!!")
        if len(candidate.contact) < 10 or len(candidate.contact) > 10:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail="Contact should be of 10 digits!!")
        Candidates.objects(id=cand_id).update_one(contact=candidate.contact)
    # if candidate.dob!=None and candidate.dob!=datetime.date(datetime.utcnow()):
    #     crud.update_candidate(candidate=candidate,cand_id=cand_id)
    if candidate.address!=None:
        if candidate.address == "":
            raise HTTPException(status_code=422, detail="Fields can't be empty!!")
        Candidates.objects(id=cand_id).update_one(address=candidate.address)
    return {"message":"Successfully Updated!!"}

@app.get("/candidates/interview-call/",dependencies=[Depends(get_current_candidate)],tags=["candidates"])
def view_interview_schedules(candidate:schemas.Candidate=Depends(get_current_candidate)):
    cand_id = candidate[0]["_id"]["$oid"]
    # cand_id = ObjectId(id)
    db_interview=json.loads(Interview.objects(cand_id=cand_id).to_json())
    if db_interview ==[]:
        raise HTTPException(status_code=404,detail="No interview scheduled!!")
    return db_interview

@app.post("/candidates/download-resume/",dependencies=[Depends(get_current_candidate)],tags=["candidates"])
def view_resume(candidate:schemas.Candidate=Depends(get_current_candidate)):
    id=candidate[0]["_id"]["$oid"]
    cand_id=ObjectId(id)
    resume=candidate[0]["resume"]
    db_cand=json.loads(Candidates.objects(id=cand_id,resume=resume).to_json())
    if db_cand==[]:
        raise HTTPException(status_code=400,detail="No resume found!!")
    if resume =="":
        raise HTTPException(status_code=400,detail="You have not uploaded resume!!")
    return FileResponse(f'files/{resume}',media_type="application/pdf",filename=resume)

@app.put("/candidates/update-resume/",dependencies=[Depends(get_current_candidate)],tags=["candidates"])
def update_resume(resume:UploadFile=File(...),candidate: schemas.Candidate = Depends(get_current_candidate)):
    id = candidate[0]["_id"]["$oid"]
    cand_id = ObjectId(id)
    if resume.content_type not in ["application/pdf","application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(400, detail="Only pdf and doc file accepted!!")
    Candidates.objects(id=cand_id).update_one(resume=resume.filename)
    file_location = f"files/{resume.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(resume.file.read())
    return "Resume successfully updated!!"

# jobs

@app.get("/Find-Jobs/",tags=["jobs"],responses={200: {
            "content": {"image/jpg": {}},
            "description": "Return an image.",
        }
    },)
def find_jobs_here():
    return FileResponse("images/img3.jpg",media_type="image/jpg")

@app.get("/jobs/{id}",tags=["jobs"])
def get_job_by_id(id):
    db_job = json.loads(Jobs.objects(id=ObjectId(id)).to_json())
    if db_job == []:
        raise HTTPException(status_code=404, detail=f"Job with id: {id} does not exist!!")
    return db_job

@app.post("/employers/jobs/",tags=["employers"],status_code=201)
          # dependencies=[Depends(get_current_employer)])
def post_job(job: schemas.JobCreate,employer: schemas.Employer = Depends(get_current_employer)):
    emp_id=employer[0]["_id"]["$oid"]
    # emp_id=ObjectId(id)
    if job.title=="" or job.post=="" or job.company_name=="" or job.job_location=="" or job.description==""\
            or job.annual_salary_in_lakhs=="" or job.apply_to=="" or job.apply_from=="":
        raise HTTPException(status_code=422,detail="Fields can't be empty!!")
    if (bool(re.match('^[a-zA-Z. ]*$', job.title)) == False):
        raise HTTPException(status_code=422, detail="Invalid value for title!!")
    if (bool(re.match('^[a-zA-Z. ]*$', job.post)) == False):
        raise HTTPException(status_code=422, detail="Invalid value for post!!")
    if (bool(re.match('^[a-zA-Z. ]*$', job.description)) == False):
        raise HTTPException(status_code=422, detail="Invalid value for description!!")
    if (bool(re.match('^[a-zA-Z. ]*$', job.company_name)) == False):
        raise HTTPException(status_code=422, detail="Invalid value for company_name!!")
    if (bool(re.match('^[0-9.]*$', job.annual_salary_in_lakhs)) == False):
        raise HTTPException(status_code=422, detail="Invalid value for annual salary!!")
    if (bool(re.match('^[a-zA-Z. ]*$', job.job_location)) == False):
        raise HTTPException(status_code=422, detail="Invalid value for job location!!")
    e1 = Jobs(title=job.title, post=job.post, description=job.description, company_name=job.company_name,
              annual_salary_in_lakhs=job.annual_salary_in_lakhs,
              job_location=job.job_location, apply_from=job.apply_from, apply_to=job.apply_to,posted_by=emp_id,status=1)
    e1.save()
    return {"message":"Job Successfully Posted!!"}

@app.get("/jobs/",tags=["jobs"])
def get_all_jobs():
    jobs = json.loads(Jobs.objects(status=1).to_json())
    if jobs==[]:
        raise HTTPException(status_code=404,detail="No Jobs Found!!")
    return jobs

@app.get("/jobs/{title}/",tags=["jobs"],status_code=200)
def search_job_by_title(title:str):
    db_job = json.loads(Jobs.objects(title=title).to_json())
    if db_job==[]:
        raise HTTPException(status_code=404, detail=f"No results found on title: {title} !!")
    return db_job


@app.get("/candidates/jobs/",dependencies=[Depends(get_current_candidate)],tags=["candidates"])
def get_applied_jobs(candidate:schemas.Candidate=Depends(get_current_candidate)):
    cand_id = candidate[0]["_id"]["$oid"]
    db_apply=json.loads(Apply.objects(cand_id=cand_id).to_json())
    if db_apply==[]:
        raise HTTPException(status_code=404,detail="Not applied for any job!!")
    return db_apply

#apply

@app.post("/candidates/apply/",status_code=201,tags=["candidates"],dependencies=[Depends(get_current_candidate)])
def apply_for_job(job_id:str,resume:UploadFile=File(...),candidate: schemas.Candidate = Depends(get_current_candidate)):
    cand_id = candidate[0]["_id"]["$oid"]
    # cand_id = ObjectId(id)
    db_job = json.loads(Jobs.objects(id=ObjectId(job_id)).to_json())

    if db_job ==[]:
        raise HTTPException(status_code=404, detail=f"Job with id: {job_id} does not exist!!")
    db_apply = json.loads(Apply.objects(job_id=job_id, cand_id=cand_id).to_json())
    if db_apply:
        raise HTTPException(status_code=409,detail="Already Applied for this job!!")
    current_date=datetime.date(datetime.now())
    # apply_to=datetime.date(str(db_job[0]["apply_to"]["$date"]))
    # apply_from=datetime.date(str(db_job[0]["apply_from"]["$date"]))
    # if (current_date < apply_from) or (current_date is apply_from):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Sorry!! apply date not started!!")
    # if (current_date) > (apply_to) or (current_date) is (apply_to):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Sorry!! apply date is over!!")
    # if resume.content_type not in ["application/pdf","application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
    #     raise HTTPException(400, detail="Only pdf and doc file accepted!!")
    file_location = f"files/{resume.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(resume.file.read())
    apply_date=str(datetime.date(datetime.now()))
    ct=Apply.objects().count()
    a_id=ct+1
    a1=Apply(job_id=job_id,cand_id=cand_id,apply_date=apply_date,id=a_id)
    a1.save()
    Candidates.objects(id=ObjectId(cand_id)).update_one(resume=resume.filename)
    return {"message":"Successfully Applied!!"}

# Admin

@app.get("/welcome_Admin/",tags=["admin"],dependencies=[Depends(get_admin)],responses={200: {
            "content": {"image/jpg": {}},
            "description": "Return an image.",
        }
    })
def welcome_admin():
    return FileResponse("images/emp4.jpg",media_type="image/jpg")

           #employers

@app.get("/admin/getemployers/",tags=["admin"],dependencies=[Depends(get_admin)])
def get_all_employers():
    employers = json.loads(Employers.objects(status=1).to_json())
    if employers == []:
        raise HTTPException(status_code=404, detail="No employers found!!!")
    num_of_emp=Employers.objects.count()

    for i in range(num_of_emp):
        yield {"_id":employers[i]["_id"]["$oid"],
            "name":employers[i]["name"],
            "email":employers[i]["email"],
            "designation": employers[i]["designation"],
    "company_name": employers[i]["company_name"],
    "contact": employers[i]["contact"],
    "address":employers[i]["address"]}

@app.get("/admin/employers/{id}/",tags=["admin"],dependencies=[Depends(get_admin)])
def get_employer_by_id(id:str):
    current_employer = json.loads(Employers.objects(id=ObjectId(id)).to_json())
    if current_employer == []:
        raise HTTPException(status_code=404, detail=f"Employer with id: {id} does not exist!!")
    return {"_id":current_employer[0]["_id"]["$oid"],
            "name":current_employer[0]["name"],
            "email":current_employer[0]["email"],
            "designation": current_employer[0]["designation"],
    "company_name": current_employer[0]["company_name"],
    "contact": current_employer[0]["contact"],
    "address":current_employer[0]["address"]}

@app.delete("/admin/employers/{id}",dependencies=[Depends(get_admin)],tags=["admin"],status_code=204)
def delete_employer(id:str):
    emp = json.loads(Employers.objects(id=ObjectId(id),status=1).to_json())
    if emp == []:
        raise HTTPException(status_code=404, detail=f"Employer with id: {id} does not exist!!!!")
    Employers.objects(id=ObjectId(id)).update_one(status=0)
    return "Successfully Deleted!!"

        # candidates


@app.get("/admin/candidates/",tags=["admin"],dependencies=[Depends(get_admin)])
def get_all_candidates():
    candidates = json.loads(Candidates.objects(status=1).to_json())
    if candidates==[]:
        raise HTTPException(status_code=404,detail="No Candidates Found!!")
    num_of_cand = Candidates.objects.count()

    for i in range(num_of_cand):
        yield {"_id": candidates[i]["_id"]["$oid"],
               "name": candidates[i]["name"],
               "email": candidates[i]["email"],
               "dob": candidates[i]["dob"],
               "grad": candidates[i]["grad"],
               "post_grad": candidates[i]["post_grad"],
               "skills": candidates[i]["skills"],
               "resume": candidates[i]["resume"],
               "contact": candidates[i]["contact"],
               "address": candidates[i]["address"]}

@app.get("/admin/candidates/{id}/",tags=["admin"],dependencies=[Depends(get_admin)])
def get_candidate_by_id(id: str):
    candidates = json.loads(Candidates.objects(id=ObjectId(id),status=1).to_json())
    if candidates == []:
        raise HTTPException(status_code=404, detail=f"Candidate with id: {id} does not exist!!")
    return {"_id": candidates[0]["_id"]["$oid"],
               "name": candidates[0]["name"],
               "email": candidates[0]["email"],
               "dob": candidates[0]["dob"],
               "grad": candidates[0]["grad"],
               "post_grad": candidates[0]["post_grad"],
               "skills": candidates[0]["skills"],
               "resume": candidates[0]["resume"],
               "contact": candidates[0]["contact"],
               "address": candidates[0]["address"]}

@app.delete("/admin/candidates/{id}/",dependencies=[Depends(get_admin)],tags=["admin"],status_code=204)
def delete_candidate(id:str):
    cand = json.loads(Candidates.objects(id=ObjectId(id), status=1).to_json())
    if cand == []:
        raise HTTPException(status_code=404, detail=f"Candidate with id: {id} does not exist!!!!")
    Candidates.objects(id=ObjectId(id)).update_one(status=0)
    return "Successfully Deleted!!"

        # jobs

@app.delete("/admin/jobs/{id}",tags=["admin"],dependencies=[Depends(get_admin)],status_code=204)
def remove_job(id:str):
    db_job = json.loads(Jobs.objects(id=ObjectId(id), status=1).to_json())
    if db_job == []:
        raise HTTPException(status_code=404, detail=f"Job with id: {id} does not exist!!!!")
    Jobs.objects(id=ObjectId(id)).update_one(status=0)
    return "Successfully Deleted!!"

        # interview

@app.get("/admin/interview/",tags=["admin"],dependencies=[Depends(get_admin)])
def view_interview_schedules():
    db_interview=json.loads(Interview.objects().to_json())
    if db_interview==[]:
        raise HTTPException(status_code=404,detail="No interview scheduled yet!!")
    return db_interview
