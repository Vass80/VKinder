import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData, delete
from sqlalchemy.orm import Session
from config import db_url_object

metadata = MetaData()
Base = declarative_base()

class Viewed(Base):
    __tablename__ = 'users_viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)

def add_to_db(prof_id, work_id):
    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        to_bd = Viewed(profile_id=prof_id, worksheet_id=work_id)
        session.add(to_bd)
        session.commit()

def read_from_db(prof_id,work_id):
    engine = create_engine(db_url_object)
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(Viewed.profile_id==prof_id).all()
        for item in from_bd:
            if item.worksheet_id == work_id:
                return(False)
    return(True)

def drop_db():
    engine = create_engine(db_url_object)
    Base.metadata.drop_all(engine)

# drop_db()
# add_to_db(1,1)
# add_to_db(1,2)
# add_to_db(1,3)
# print(read_from_db(1,4))
