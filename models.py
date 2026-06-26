from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    url = Column(String)
    seo_score = Column(Integer)
    gseo_score = Column(Integer)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )