from datetime import datetime, timedelta
from typing import List

from sqlalchemy import and_, or_, extract
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(db: Session, user: User, name: str = None, last_name: str = None, email: str = None) -> List[Contact]:

    queries = []

    if name:
        queries.append(Contact.name == name)
    if last_name:
        queries.append(Contact.last_name == last_name)
    if email:
        queries.append(Contact.email == email)

    contacts = db.query(Contact).filter(and_(*queries, Contact.user_id == user.id)).all()
    return contacts


async def get_contacts_birthdays(db: Session, user: User) -> List[Contact]:

    today = datetime.now().date()
    last_day = today + timedelta(days=7)

    dates = db.query(Contact).filter(or_
                                        (and_(extract('month', Contact.born_date) == last_day.month,
                                               extract('day', Contact.born_date) <= last_day.day,
                                               Contact.user_id == user.id),
                                               

                                        and_(extract('month', Contact.born_date) == today.month,
                                               extract('day', Contact.born_date) >= today.day,
                                               Contact.user_id == user.id))).all()

    return dates


async def get_contact(contact_id: int, db: Session, user: User) -> Contact:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactModel, db: Session, user: User) -> Contact:

    contact = Contact(name = body.name, last_name = body.last_name, email = body.email, phone = body.phone, born_date = body.born_date, user = user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactModel, db: Session, user: User) -> Contact | None:

    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()

    if contact:
        contact.name = body.name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.born_date = body.born_date
        db.commit()
    return contact


async def remove_contact(contact_id: int, db: Session, user: User)  -> Contact | None:

    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    
    if contact:
        db.delete(contact)
        db.commit()
    return contact
