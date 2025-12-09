from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    title = Column(
        String(255),
        nullable=False
    )
    description = Column(
        Text,
        nullable=True
    )
    is_important = Column(
        Boolean,
        nullable=False,
        default=False
    )
    deadline_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    quadrant = Column(
        String(2),
        nullable=False
    )
    completed = Column(
        Boolean,
        nullable=False,
        default=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    owner = relationship(
        "User",
        back_populates="tasks"
    )

    def __repr__(self) -> str:
        return (
            f"<Task(id={self.id}, title='{self.title[:30]}...', "
            f"quadrant='{self.quadrant}', completed={self.completed})>"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_important": self.is_important,
            "is_urgent": self.is_urgent,
            "quadrant": self.quadrant,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "user_id": self.user_id
        }