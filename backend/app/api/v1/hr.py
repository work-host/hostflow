from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import get_db
from app.models import User, EmployeeProfile, EmploymentTerm
from app.core.security import hash_password
from app.schemas.hr import CreateUserProfileIn
from app.deps import get_current_user, require_roles

router = APIRouter(prefix="/hr", tags=["hr"])


@router.get("/employees")
def list_employees(
    db: Session = Depends(get_db), current: User = Depends(get_current_user)
):
    tenant_id = current.tenant_id
    rows = db.execute(
        select(User, EmployeeProfile).where(
            User.id == EmployeeProfile.user_id, User.tenant_id == tenant_id
        )
    ).all()
    out = []
    for u, p in rows:
        out.append(
            {
                "user": {
                    "id": u.id,
                    "email": u.email,
                    "role": u.role,
                    "is_active": u.is_active,
                },
                "profile": {
                    "first_name": p.first_name,
                    "last_name": p.last_name,
                    "middle_name": p.middle_name,
                    "phone": p.phone,
                    "telegram": p.telegram,
                    "position": p.position,
                    "employment_type": p.employment_type,
                    "manager_id": p.manager_id,
                    "hire_date": p.hire_date,
                    "fire_date": p.fire_date,
                },
            }
        )
    return out


@router.post("/users", status_code=201)
def create_user_with_profile(
    payload: CreateUserProfileIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "lead_recruiter")),
    current: User = Depends(get_current_user),
):
    tenant_id = current.tenant_id
    exists = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )
    u = User(
        tenant_id=tenant_id,
        email=str(payload.email),
        role=payload.role,
        is_active=payload.is_active,
    )
    if payload.password:
        try:
            u.password_hash = hash_password(payload.password)
        except Exception:
            pass
    db.add(u)
    db.commit()
    db.refresh(u)

    p = EmployeeProfile(
        tenant_id=tenant_id,
        user_id=u.id,
        first_name=payload.profile.first_name,
        last_name=payload.profile.last_name,
        middle_name=payload.profile.middle_name,
        phone=payload.profile.phone,
        telegram=payload.profile.telegram,
        position=payload.profile.position,
        employment_type=payload.profile.employment_type,
        manager_id=payload.profile.manager_id,
        hire_date=payload.profile.hire_date,
        fire_date=payload.profile.fire_date,
    )
    db.add(p)

    if payload.terms:
        t = EmploymentTerm(
            tenant_id=tenant_id,
            user_id=u.id,
            valid_from=payload.terms.valid_from,
            valid_to=payload.terms.valid_to,
            salary_monthly=payload.terms.salary_monthly,
            bonus_scheme_code=payload.terms.bonus_scheme_code,
            work_hours_per_week=payload.terms.work_hours_per_week,
            currency=payload.terms.currency,
            comment=payload.terms.comment,
        )
        db.add(t)

    db.commit()
    return {"status": "ok", "user_id": u.id}
