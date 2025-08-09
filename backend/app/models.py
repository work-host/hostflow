# ruff: noqa: E402
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from .db import Base


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"))
    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(50), nullable=False)
    # languages хранится в БД как ARRAY; ORM-тип можно опустить (не используем тут)
    is_active = Column(Boolean, server_default=text("true"))
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
    tenant = relationship("Tenant")
    password_hash = Column(String, nullable=True)


class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(
        Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    stage_code = Column(
        String(50), nullable=False, default="new"
    )  # ссылается на stages.code (логически)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))

    tenant = relationship("Tenant")


# --- HR models ---
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from app.db import Base


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    phone = Column(String)
    telegram = Column(String)
    position = Column(String)
    employment_type = Column(String)
    manager_id = Column(Integer, ForeignKey("users.id"))
    hire_date = Column(Date)
    fire_date = Column(Date)
    user = relationship("User", foreign_keys=[user_id])
    manager = relationship("User", foreign_keys=[manager_id])


class EmploymentTerm(Base):
    __tablename__ = "employment_terms"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date)
    salary_monthly = Column(Numeric(12, 2))
    bonus_scheme_code = Column(String)
    work_hours_per_week = Column(Integer)
    currency = Column(String(8))
    comment = Column(Text)
