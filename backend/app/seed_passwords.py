from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.core.security import hash_password
from app.models import User

SEED = {
  "biuro@work-host.com": "ChangeMe123!",
  "valentyna.l@work-host.com": "ChangeMe123!",
  "roman.k@work-host.com": "ChangeMe123!",
  "olha.p@work-host.com": "ChangeMe123!",
  "anastasiya.d@work-host.com": "ChangeMe123!",
  "iryna.y@work-host.com": "ChangeMe123!",
  "victoria.t@work-host.com": "ChangeMe123!",
}

def run():
    with SessionLocal() as s:  # type: Session
        for email, pw in SEED.items():
            u = s.query(User).filter(User.email == email).first()
            if u and not u.password_hash:
                u.password_hash = hash_password(pw)
                s.add(u)
        s.commit()
        print("✅ Password seed ensured")

if __name__ == "__main__":
    run()
