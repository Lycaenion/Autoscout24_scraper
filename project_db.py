from datetime import date

import sqlite3

from sqlalchemy import (
    String, create_engine, select, delete
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, Session
)


class Base(MappedAsDataclass, DeclarativeBase):
    """Subclasses will be converted into dataclasses"""

class Advertisements(Base):

    __tablename__ = 'Advertisements'
    __table_args__ = {'sqlite_autoincrement': True}

    id : Mapped[int]= mapped_column(init=False, primary_key=True, autoincrement=True)
    url : Mapped[str]= mapped_column(String(300),nullable=False, unique=True)
    brand: Mapped[str]= mapped_column(String(100),nullable=False)
    model_version: Mapped[str]= mapped_column(String(100),nullable=True)
    year: Mapped[str]= mapped_column(String(100),nullable=True)
    price: Mapped[str]= mapped_column(String(100),nullable=True)
    milage: Mapped[str]= mapped_column(String(100),nullable=True)
    gearbox: Mapped[str]= mapped_column(String(100),nullable=True)
    fuel_type: Mapped[str]= mapped_column(String(100),nullable=True)
    engine_power: Mapped[str]= mapped_column(String(100),nullable=True)
    location: Mapped[str]= mapped_column(String(100),nullable=True)
    date_added: Mapped[str]= mapped_column(String(100),default=None, nullable=False, comment='date added to db')

def add_to_db(url, brand, model_version, year, price, milage, gearbox, fuel_type, engine_power, location):
    SQLALCHEMY_URI = 'sqlite:///db.sqlite'
    engine = create_engine(SQLALCHEMY_URI, echo=True, echo_pool='debug')
    Base.metadata.create_all(engine)

    in_db = check_if_post_exists_in_db(url, engine)

    if in_db is False:

        with Session(engine) as session:
            date_added = date.today().isoformat()

            advert = Advertisements(url, brand, model_version, year, price,milage, gearbox, fuel_type, engine_power, location, date_added)
            session.add(advert)
            session.commit()
            print('added advertisement')

def check_if_post_exists_in_db(url, engine):
    with Session(engine) as session:
        stmt = select(Advertisements).where(Advertisements.url == url)
        result = session.execute(stmt).scalar()
        if result is None:
            print('no advertisement')
            return False
        else:
            print('found advertisement')
            return True

if __name__ == '__main__':
    SQLALCHEMY_URI = 'sqlite:///db.sqlite'
    engine = create_engine(SQLALCHEMY_URI, echo=True, echo_pool='debug')
    Base.metadata.create_all(engine)