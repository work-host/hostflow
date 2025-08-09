from sqlalchemy import text, select
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Tenant, Candidate

TENANT_NAME = "Work Host International"

USERS = [
    ("biuro@work-host.com", "admin"),
    ("valentyna.l@work-host.com", "lead_recruiter"),
    ("roman.k@work-host.com", "recruiter"),
    ("olha.p@work-host.com", "recruiter"),
    ("anastasiya.d@work-host.com", "recruiter"),
    ("iryna.y@work-host.com", "recruiter"),
    ("victoria.t@work-host.com", "marketing"),
]


def upsert_tenant(session: Session) -> int:
    t = session.execute(
        select(Tenant).where(Tenant.name == TENANT_NAME)
    ).scalar_one_or_none()
    if t:
        return t.id
    t = Tenant(name=TENANT_NAME)
    session.add(t)
    session.commit()
    session.refresh(t)
    return t.id


def upsert_users(session: Session, tenant_id: int):
    for email, role in USERS:
        exists = session.execute(
            text("select 1 from users where email=:e"), {"e": email}
        ).first()
        if not exists:
            session.execute(
                text(
                    "insert into users(tenant_id,email,role,is_active) values(:t,:e,:r,true)"
                ),
                {"t": tenant_id, "e": email, "r": role},
            )
    session.commit()


def seed_candidates(session: Session, tenant_id: int):
    # добавим парочку демо-кандидатов, если пусто
    count = session.execute(
        text("select count(*) from candidates where tenant_id=:t"), {"t": tenant_id}
    ).scalar()
    if count == 0:
        session.add_all(
            [
                Candidate(
                    tenant_id=tenant_id,
                    full_name="Ivan Petrov",
                    phone="+48 600 000 001",
                    stage_code="new",
                ),
                Candidate(
                    tenant_id=tenant_id,
                    full_name="Pavel Ivanov",
                    phone="+48 600 000 002",
                    stage_code="contacted",
                ),
            ]
        )
        session.commit()


if __name__ == "__main__":
    with SessionLocal() as s:
        tenant_id = upsert_tenant(s)
        upsert_users(s, tenant_id)
        seed_candidates(s, tenant_id)
        print("✅ Seed done for tenant_id:", tenant_id)
