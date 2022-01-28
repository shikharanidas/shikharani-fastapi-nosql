from datetime import datetime, date

from sqlalchemy import or_
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import models, schemas
from fastapi import HTTPException,status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# employers

def get_employer(db: Session, emp_id: int):
    return db.query(models.Employer).filter(models.Employer.emp_id == emp_id,models.Employer.status==1).first()

def get_employer_by_email(db: Session, email: str):
    return db.query(models.Employer).filter(models.Employer.email == email,models.Employer.status==1).first()

def get_employer_by_email1(email: str):
    return db.query(models.Employer).filter(models.Employer.email == email,models.Employer.status==1).first()

def get_employers(db: Session):
    # return db.query(models.Employer).offset(0).limit(100).all()
    return db.query(models.Employer).filter(models.Employer.status == 1).all()

def create_employer(db: Session, employer: schemas.EmployerCreate):
    fake_hashed_password = get_password_hash(employer.password)
    db_employer = models.Employer(
        name=employer.name,
        designation=employer.designation,
        company_name=employer.company_name,
        contact=employer.contact,
        address=employer.address,
        email=employer.email,
        hashed_password=fake_hashed_password)
    db.add(db_employer)
    db.commit()
    db.refresh(db_employer)
    return db_employer

def update_employer(db: Session, employer: schemas.EmployerUpdate,emp_id:int):
    if employer.name!=None:
        db.query(models.Employer).filter(models.Employer.emp_id == emp_id).\
            update({models.Employer.name:employer.name},synchronize_session=False)
    if employer.designation != None:
        db.query(models.Employer).filter(models.Employer.emp_id == emp_id). \
            update({models.Employer.designation: employer.designation}, synchronize_session=False)
    if employer.company_name != None:
        db.query(models.Employer).filter(models.Employer.emp_id == emp_id). \
            update({models.Employer.company_name: employer.company_name}, synchronize_session=False)
    if employer.contact != None:
        db.query(models.Employer).filter(models.Employer.emp_id == emp_id). \
            update({models.Employer.contact: employer.contact}, synchronize_session=False)
    if employer.address != None:
        db.query(models.Employer).filter(models.Employer.emp_id == emp_id). \
            update({models.Employer.address: employer.address}, synchronize_session=False)
    db.commit()

    return True

def get_posted_jobs(db:Session,emp_id:int):
    return db.query(models.Jobs).filter(models.Jobs.posted_by==emp_id).all()

# candidates

def get_candidate(db: Session, cand_id: int):
    return db.query(models.Candidate).filter(models.Candidate.cand_id == cand_id,models.Candidate.status==1).first()

def get_candidate_by_email(db: Session, email: str):
    return db.query(models.Candidate).filter(models.Candidate.email == email,models.Candidate.status==1).first()

def get_candidate_by_email1(db: Session, email: str):
    return db.query(models.Candidate).filter(models.Candidate.email == email).first()

def get_candidates(db: Session):
    # return db.query(models.Candidate).offset(0).limit(100).all()
    return db.query(models.Candidate).filter(models.Candidate.status == 1).all()

def get_candidate_by_skills(db:Session,skills:str):
    return db.query(models.Candidate.cand_id,
                    models.Candidate.name,
                    models.Candidate.email,
                    models.Candidate.dob,
                    models.Candidate.contact,
                    models.Candidate.grad,
                    models.Candidate.post_grad,
                    models.Candidate.address,
                    models.Skills.skill1,
                    models.Skills.skill2,
                    models.Skills.skill3,
                    models.Skills.skill4).join(models.Skills,models.Candidate.cand_id==models.Skills.cand_id)\
        .filter(or_(models.Skills.skill1==skills.lower(),models.Skills.skill2==skills.lower(),
                    models.Skills.skill3==skills.lower(),models.Skills.skill4==skills.lower())).all()

def create_candidate(db: Session, candidate: schemas.CandidateCreate):
    fake_hashed_password = get_password_hash(candidate.password)
    db_candidate = models.Candidate(
        name=candidate.name,
        email=candidate.email,
        dob=candidate.dob,
        grad=candidate.grad,
        post_grad=candidate.post_grad,
        # skills=candidate.skills,
        contact=candidate.contact,
        address=candidate.address,
              hashed_password=fake_hashed_password)
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

def update_candidate(db: Session, candidate: schemas.CandidateUpdate,cand_id:int):
    if candidate.name!=None:
        db.query(models.Candidate).filter(models.Candidate.cand_id == cand_id).\
            update({models.Candidate.name:candidate.name},synchronize_session=False)
    if candidate.contact != None:
        db.query(models.Candidate).filter(models.Candidate.cand_id == cand_id). \
            update({models.Candidate.contact: candidate.contact}, synchronize_session=False)
    # if candidate.dob!=None:
    #     db.query(models.Candidate).filter(models.Candidate.cand_id == cand_id).\
    #         update({models.Candidate.dob:candidate.dob},synchronize_session=False)
    if candidate.address!=None:
        db.query(models.Candidate).filter(models.Candidate.cand_id == cand_id).\
            update({models.Candidate.address:candidate.address},synchronize_session=False)
    if candidate.grad!=None:
        db.query(models.Candidate).filter(models.Candidate.cand_id == cand_id).\
            update({models.Candidate.grad:candidate.grad},synchronize_session=False)
    if candidate.post_grad!=None:
        db.query(models.Candidate).filter(models.Candidate.cand_id == cand_id).\
            update({models.Candidate.post_grad:candidate.post_grad},synchronize_session=False)
    if candidate.skills!=None:
        db.query(models.Candidate).filter(models.Candidate.cand_id == cand_id).\
            update({models.Candidate.skills:candidate.skills},synchronize_session=False)
    db.commit()
    return True

def create_cand_skills(db:Session,cand_id:int,skill1:str,skill2:str,skill3:str,skill4:str):
    db_cand_skills=models.Skills(skill1=skill1,
                                 skill2=skill2,
                                 skill3=skill3,
                                 skill4=skill4,
                                 cand_id=cand_id)
    db.add(db_cand_skills)
    db.commit()
    db.refresh(db_cand_skills)
    return db_cand_skills

def get_applied_jobs(db:Session,cand_id:int):
    db_apply = db.query(models.Apply).filter(models.Apply.cand_id == cand_id).all()
    if db_apply is None:
        raise HTTPException(status_code=404, detail="No applied jobs!!")
    return db.query(models.Jobs).filter(models.Jobs.job_id.in_([f.job_id for f in db_apply])).all()

def update_resume(db:Session,cand_id:int,resume:str):
    db.query(models.Candidate).filter(models.Candidate.cand_id == cand_id). \
        update({models.Candidate.resume: resume}, synchronize_session=False)
    db.commit()
    return True

# jobs

def get_jobs(db: Session):
    # return db.query(models.Jobs).offset(0).limit(100).all()
    return db.query(models.Jobs).filter(models.Jobs.status == 1).all()

def get_job(db: Session, job_id: int):
    return db.query(models.Jobs).filter(models.Jobs.job_id == job_id).first()

def get_jobs_by_title(db: Session,title:str):
    t= db.query(models.Jobs.title).all()
    # for f in range(len(t)):
    #     t[f]=t[f].lower()
    # for i in t:
    #     if i.lower() == title.lower():
    #         yield db.query(models.Jobs).filter(models.Jobs.title == title.lower()).all()
    #        db.query(models.Jobs).filter(models.Jobs.title == title.lower()).all(),\
    return db.query(models.Jobs).filter(models.Jobs.title == title.lower()).all()
    # return db.query(models.Jobs).filter(title.lower()==[t[f] for f in range(len(t))]).all()

def create_job(db: Session, job: schemas.JobCreate, emp_id: int):
    db_job = models.Jobs(title=job.title,
                         post=job.post,
                         job_location=job.job_location,
                         company_name=job.company_name,
                         description=job.description,
                         annual_salary_in_lakhs=job.annual_salary_in_lakhs,
                         apply_to=job.apply_to,
                         apply_from=job.apply_from,
                         posted_by=emp_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
#
# def create_job(db: Session, job: schemas.JobCreate,apply_to:date,apply_from:date, emp_id: int):
#     db_job = models.Jobs(title=job.title,
#     post=job.post,
#                          job_location=job.job_location,
#                          company_name=job.company_name,
#                          description=job.description,
#                          annual_salary_in_lakhs=job.annual_salary_in_lakhs,
#                          apply_to=apply_to,
#                          apply_from=apply_from,
#     posted_by=emp_id)
#     db.add(db_job)
#     db.commit()
#     db.refresh(db_job)
#     return db_job

def check_posted_jobs(db:Session,job_id:int,emp_id:int):
    return db.query(models.Jobs).filter(models.Jobs.job_id == job_id,models.Jobs.posted_by==emp_id).first()

# apply

def apply_job(db: Session, job_id: int,cand_id:int,resume:str,apply_date:str=datetime.date(datetime.utcnow())):
    db_job = models.Apply(cand_id=cand_id,job_id=job_id,apply_date=apply_date)
    db.add(db_job)
    db.query(models.Candidate).filter(models.Candidate.cand_id == cand_id). \
        update({models.Candidate.resume: resume}, synchronize_session=False)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_apply_info(db:Session,job_id:int,cand_id:int):
    return db.query(models.Apply).filter(models.Apply.cand_id==cand_id,models.Apply.job_id==job_id).first()

def get_applied_candidates(db,job_id:int):
    db_apply=db.query(models.Apply).filter(models.Apply.job_id==job_id).all()
    if db_apply is None:
        raise HTTPException(status_code=404,detail="No candidates found!!")
    return db.query(models.Candidate.cand_id,
                    models.Candidate.name,
                    models.Candidate.email,
                    models.Candidate.dob,
                    models.Candidate.contact,
                    models.Candidate.grad,
                    models.Candidate.post_grad,
                    models.Candidate.address,
                    models.Candidate.resume,
                    models.Skills.skill1,
                    models.Skills.skill2,
                    models.Skills.skill3,
                    models.Skills.skill4).join(models.Skills,models.Skills.cand_id==models.Candidate.cand_id).\
        filter(models.Candidate.cand_id.in_([f.cand_id for f in db_apply]),models.Candidate.status==1).all()

# admin

def get_admin(db: Session, userid: str):
    return db.query(models.Admin).filter(models.Admin.userid == userid).first()

def delete_job(db:Session,job_id:int):
    # db.query(models.Jobs).filter(models.Jobs.job_id==job_id).delete(synchronize_session=False)
    db.query(models.Jobs).filter(models.Jobs.job_id == job_id). \
        update({models.Jobs.status: 0}, synchronize_session=False)
    db.commit()
    return True

def delete_candidate(db:Session,cand_id:int):
    db.query(models.Candidate).filter(models.Candidate.cand_id==cand_id).\
            update({models.Candidate.status: 0}, synchronize_session=False)
    db.commit()
    return True

def delete_employer(db:Session,emp_id:int):
    db.query(models.Employer).filter(models.Employer.emp_id==emp_id).\
            update({models.Employer.status: 0}, synchronize_session=False)
    db.commit()
    return True

# interview

def create_interview(db:Session,interview: schemas.InterviewCreate,job_id:int,cand_id:int,emp_id: int):
    db_interview = models.Interview(venue=interview.venue,
                         day=interview.day,
                         time=interview.time,
                         message=interview.message,
                         job_id=job_id,
                         cand_id=cand_id,
                         emp_id=emp_id)
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    return db_interview

def get_interview_info(db:Session,cand_id:int):
    return db.query(models.Interview.message,
                models.Interview.venue,
                models.Interview.day,
                models.Interview.time,
                models.Interview.job_id,
                models.Jobs.title,
                models.Jobs.post,
                models.Jobs.company_name
                ).join(models.Jobs,models.Interview.job_id==models.Jobs.job_id).\
        filter(models.Interview.cand_id==cand_id).all()

def check_interview_schedule(db:Session,job_id:int,cand_id:int):
    db_interview_schedule=db.query(models.Interview).filter(models.Interview.job_id==job_id,
                                                            models.Interview.cand_id==cand_id).first()
    return db_interview_schedule

def get_interview_schedules(db:Session):
    return db.query(
                models.Interview.venue,
                models.Interview.day,
                models.Interview.time,
                models.Interview.message,
                models.Interview.job_id,
                models.Jobs.title,
                models.Jobs.post,
                models.Jobs.company_name,
                models.Candidate.name,
                models.Candidate.cand_id,
                models.Interview.emp_id).join(models.Jobs,models.Interview.job_id==models.Jobs.job_id).\
    join(models.Candidate,models.Interview.cand_id==models.Candidate.cand_id).all()

def get_all_interview_schedules(emp_id:int,db:Session):
    return db.query(
                models.Interview.venue,
                models.Interview.day,
                models.Interview.time,
                models.Interview.message,
                models.Interview.job_id,
                models.Jobs.title,
                models.Jobs.post,
                models.Jobs.company_name,
                models.Candidate.name,
                models.Candidate.cand_id,
                models.Interview.emp_id).join(models.Jobs,models.Interview.job_id==models.Jobs.job_id).\
    join(models.Candidate,models.Interview.cand_id==models.Candidate.cand_id).\
        filter(models.Interview.emp_id==emp_id).all()