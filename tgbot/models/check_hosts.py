from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, insert, null, update, func, delete
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
import datetime

from tgbot.models.users import User
from tgbot.services.db_base import Base

class Hosts(Base):
    __tablename__ = "hosts"
    id = Column(Integer, primary_key=True)
    user = Column(ForeignKey(User.telegram_id, ondelete='CASCADE'))
    hostname = Column(String(length=100))
    status = Column(Boolean, nullable=True)
    last_change = Column(DateTime)

    @classmethod
    async def get_hosts(cls, session_maker: sessionmaker, telegram_id: int) -> 'Hosts':
        """ Gets all hosts by user id """
        async with session_maker() as db_session:
            sql = select(cls).where(cls.user == telegram_id)
            request = await db_session.execute(sql)
            host: cls = request.scalars()
        return host

    @classmethod
    async def get_host(cls, session_maker: sessionmaker, id: int) -> 'Hosts':
        """ Gets host by id """
        async with session_maker() as db_session:
            sql = select(cls).where(cls.id == id)
            request = await db_session.execute(sql)
            host: cls = request.scalars()
        return request.first()

    @classmethod
    async def add_host(cls,
                       session_maker: sessionmaker,
                       telegram_id: int,
                       hostname: str,
                       last_change: datetime = datetime.datetime.now()
                       ) -> 'Hosts':
        """ Adds host to db """
        async with session_maker() as db_session:
            sql = insert(cls).values(user=telegram_id,
                                     hostname=hostname,
                                     last_change=last_change).returning('*')
            result = await db_session.execute(sql)
            await db_session.commit()
            return result.first()

    @classmethod
    async def del_host(cls,
                       session_maker: sessionmaker,
                       telegram_id: int,
                       host_id: str,
                       ) -> 'Hosts':
        """ Delete host from db """
        async with session_maker() as db_session:
            sql = delete(cls).where(cls.user == telegram_id,
                                    cls.id == host_id).returning('*')
            result = await db_session.execute(sql)
            await db_session.commit()
            return result.first()