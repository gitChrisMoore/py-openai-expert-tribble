import uuid
from sqlalchemy import Table, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

DB_FILEPATH = "py_backend/storage/data_base.db"

Base = declarative_base()

blueprint_objective_association = Table(
    "blueprint_objective",
    Base.metadata,
    Column("blueprint_id", String(36), ForeignKey("blueprint_dev.blueprint_id")),
    Column("objective_id", String(36), ForeignKey("objective_dev.objective_id")),
)


class Blueprint(Base):
    """Defines the blueprint table."""

    __tablename__ = "blueprint_dev"
    blueprint_id = Column(
        String(36),
        primary_key=True,
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    blueprint_name = Column(String, nullable=False)
    blueprint_description = Column(String, nullable=False)
    sub_topic_name = Column(String, nullable=False)
    pub_topic_name = Column(String, nullable=False)
    initial_context = Column(String, nullable=False)
    # Define the one-to-many relationship
    blueprint_objectives = relationship(
        "Objective",
        secondary=blueprint_objective_association,
        back_populates="blueprints",
    )


class Objective(Base):
    """Defines the objective table."""

    __tablename__ = "objective_dev"

    objective_id = Column(
        String(36),
        primary_key=True,
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    objective_name = Column(String, nullable=False)
    objective_description = Column(String, nullable=False)
    parameters = Column(String, nullable=False)

    blueprints = relationship(
        "Blueprint",
        secondary=blueprint_objective_association,
        back_populates="blueprint_objectives",
    )
