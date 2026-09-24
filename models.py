from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class EventType(Base):
    """Тип мероприятия. Расширяемый — добавляется через бота."""
    __tablename__ = "event_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    events: Mapped[list["Event"]] = relationship(back_populates="event_type")


class Responsible(Base):
    """Ответственный за мероприятие."""
    __tablename__ = "responsibles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), index=True)

    events: Mapped[list["Event"]] = relationship(back_populates="responsible")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    reg_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    type_id: Mapped[int] = mapped_column(ForeignKey("event_types.id"))
    responsible_id: Mapped[int] = mapped_column(ForeignKey("responsibles.id"))

    event_type: Mapped[EventType] = relationship(back_populates="events")
    responsible: Mapped[Responsible] = relationship(back_populates="events")

    @property
    def date_key(self) -> str:
        return self.start_at.strftime("%Y-%m-%d")