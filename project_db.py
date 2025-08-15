from datetime import date

import sqlite3

from sqlalchemy import (
    String, create_engine, select, delete, ForeignKey, Integer
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, Session, relationship, sessionmaker
)
from typing import List, Optional


class Base(MappedAsDataclass, DeclarativeBase):
    """Subclasses will be converted into dataclasses"""

class Webpage(Base):
    """Webpages"""
    __tablename__ = "Webpages"
    __table_args__ = {'sqlite_autoincrement': True}

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    site_name : Mapped[str] = mapped_column(String(50), nullable=False)
    advertisements: Mapped[Optional[List["Advertisement"]]] = relationship(
        back_populates="webpage",
        default_factory=list
    )

class Advertisement(Base):

    __tablename__ = 'Advertisements'
    __table_args__ = {'sqlite_autoincrement': True}

    id : Mapped[int]= mapped_column(init=False, primary_key=True, autoincrement=True)
    url : Mapped[str]= mapped_column(String(300),nullable=False, unique=True)
    webpage_id : Mapped[int] = mapped_column(ForeignKey('Webpages.id'), nullable=False)
    webpage : Mapped[Webpage] = relationship(back_populates='advertisements')
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

    with Session(engine) as session:
        date_added = date.today().isoformat()

        advert = Advertisement(url, brand, model_version, year, price,milage, gearbox, fuel_type, engine_power, location, date_added)
        session.add(advert)
        session.commit()
        print('added advertisement')

def check_if_post_exists_in_db(url):
    SQLALCHEMY_URI = 'sqlite:///db.sqlite'
    engine = create_engine(SQLALCHEMY_URI, echo=True, echo_pool='debug')

    with Session(engine) as session:
        stmt = select(Advertisement).where(Advertisement.url == url)
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
    webpage1 = Webpage(site_name='Bazos')
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(webpage1)
    session.commit()
