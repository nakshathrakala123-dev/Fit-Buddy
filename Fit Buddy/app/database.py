from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, joinedload, relationship, sessionmaker

from .config import DB_PATH

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(60), nullable=False)
    age = Column(Integer)
    weight = Column(Float)
    goal = Column(String(200))
    intensity = Column(String(10))
    plan = relationship("WorkoutPlan", uselist=False, back_populates="user", cascade="all, delete-orphan")


class WorkoutPlan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text)
    nutrition_tip = Column(Text)
    user = relationship("User", back_populates="plan")


def init_db():
    Base.metadata.create_all(engine)


def save_user(user_id, name, age, weight, goal, intensity):
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is None:
            user = User(id=user_id)
            db.add(user)
        user.name, user.age, user.weight = name, age, weight
        user.goal, user.intensity = goal, intensity
        db.commit()


def save_plan(user_id, plan, tip=""):
    """Store a fresh plan. A returning user ID replaces the old plan."""
    with SessionLocal() as db:
        row = db.query(WorkoutPlan).filter_by(user_id=user_id).first()
        if row is None:
            db.add(WorkoutPlan(user_id=user_id, original_plan=plan, nutrition_tip=tip))
        else:
            row.original_plan, row.updated_plan, row.nutrition_tip = plan, None, tip
        db.commit()


def update_plan(user_id, updated_text, tip=None):
    with SessionLocal() as db:
        row = db.query(WorkoutPlan).filter_by(user_id=user_id).first()
        if row:
            row.updated_plan = updated_text
            if tip:
                row.nutrition_tip = tip
            db.commit()


def get_original_plan(user_id):
    plan = get_plan(user_id)
    return plan.original_plan if plan else None


def get_plan(user_id):
    with SessionLocal() as db:
        return db.query(WorkoutPlan).filter_by(user_id=user_id).first()


def get_user(user_id):
    with SessionLocal() as db:
        return db.get(User, user_id)


def get_all_users():
    with SessionLocal() as db:
        return db.query(User).options(joinedload(User.plan)).order_by(User.id).all()


def delete_user(user_id):
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user:
            db.delete(user)
            db.commit()
