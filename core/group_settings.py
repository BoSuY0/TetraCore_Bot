from sqlalchemy import create_engine, Column, Integer, BigInteger, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    owner_id = Column(BigInteger, nullable=False)
    active_module = Column(String(255))

class GroupSettings:
    def __init__(self, db_url="sqlite:///bot.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_group(self, chat_id: int, owner_id: int, active_module: str = None):
        session = self.Session()
        group = session.query(Group).filter_by(chat_id=chat_id).first()

        if group:
            group.owner_id = owner_id
            group.active_module = active_module
        else:
            group = Group(chat_id=chat_id, owner_id=owner_id, active_module=active_module)
            session.add(group)
        
        session.commit()
        session.close()

    def get_group(self, chat_id: int):
        session = self.Session()
        group = session.query(Group).filter_by(chat_id=chat_id).first()
        session.close()
        return group

    def save_active_module(self, chat_id: int, module_name: str):
        session = self.Session()
        group = session.query(Group).filter_by(chat_id=chat_id).first()
        
        if group:
            group.active_module = module_name
            session.commit()
        session.close()

    def get_active_module(self, chat_id: int) -> str:
        group = self.get_group(chat_id)
        return group.active_module if group else None

    def get_owner_id(self, chat_id: int) -> int:
        group = self.get_group(chat_id)
        return group.owner_id if group else None
