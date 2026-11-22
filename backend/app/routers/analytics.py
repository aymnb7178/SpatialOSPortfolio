from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import SiteLink, VisitEvent

router = APIRouter(tags=["analytics"])

@router.post("/analytics/visit", status_code=204)
def record_visit(data: dict, db: Session = Depends(get_db)):
    session_key = str(data.get("session_key", ""))[:80].strip()
    if not session_key:
        return
    item = VisitEvent(
        session_key=session_key,
        path=str(data.get("path", "/"))[:255] or "/",
        user_agent=str(data.get("user_agent", ""))[:500],
    )
    db.add(item)
    db.commit()

@router.get("/site-links")
def public_links(db: Session = Depends(get_db)):
    return [
        {"id": item.id, "label": item.label, "url": item.url, "channel": item.channel}
        for item in db.scalars(
            select(SiteLink).where(SiteLink.is_active.is_(True)).order_by(SiteLink.sort_order, SiteLink.id)
        )
    ]
