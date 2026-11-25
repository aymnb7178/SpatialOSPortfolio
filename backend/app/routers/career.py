import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..database import get_db
from ..models import CareerEntry, Skill, User
from ..schemas import CareerCreate, CareerOut, CareerUpdate, SkillCreate, SkillOut, SkillUpdate

router = APIRouter(prefix="/career", tags=["career"])
admin_router = APIRouter(prefix="/admin/career", tags=["admin-career"])
skills_router = APIRouter(prefix="/skills", tags=["skills"])
admin_skills_router = APIRouter(prefix="/admin/skills", tags=["admin-skills"])


def _json(value):
    try:
        return json.loads(value or "[]")
    except (TypeError, ValueError):
        return []


def _career_payload(item: CareerEntry) -> dict:
    data = {column.name: getattr(item, column.name) for column in CareerEntry.__table__.columns}
    data["tags"] = _json(item.tags_json)
    data["related_projects"] = _json(item.related_projects_json)
    data.pop("tags_json", None)
    data.pop("related_projects_json", None)
    return data


def _skill_payload(item: Skill) -> dict:
    data = {column.name: getattr(item, column.name) for column in Skill.__table__.columns}
    data["related_projects"] = _json(item.related_projects_json)
    data["related_certificates"] = _json(item.related_certificates_json)
    data.pop("related_projects_json", None)
    data.pop("related_certificates_json", None)
    return data


def _apply(item, data: dict, fields: tuple[str, ...]) -> None:
    for field in fields:
        if field in data:
            value = data[field]
            setattr(item, field, value.strip() if isinstance(value, str) else value)


def _apply_career(item: CareerEntry, data: dict):
    _apply(item, data, ("kind", "period", "title", "title_ar", "organization", "organization_ar", "description", "description_ar", "sort_order", "is_visible"))
    if "tags" in data:
        item.tags_json = json.dumps(data["tags"], ensure_ascii=False)
    if "related_projects" in data:
        item.related_projects_json = json.dumps(data["related_projects"], ensure_ascii=False)


def _apply_skill(item: Skill, data: dict):
    _apply(item, data, ("name", "name_ar", "category", "category_ar", "level", "description", "description_ar", "sort_order", "is_visible"))
    if "related_projects" in data:
        item.related_projects_json = json.dumps(data["related_projects"], ensure_ascii=False)
    if "related_certificates" in data:
        item.related_certificates_json = json.dumps(data["related_certificates"], ensure_ascii=False)


@router.get("", response_model=list[CareerOut])
def public_career(db: Session = Depends(get_db)):
    items = db.scalars(select(CareerEntry).where(CareerEntry.is_visible.is_(True)).order_by(CareerEntry.sort_order, CareerEntry.id)).all()
    return [_career_payload(item) for item in items]


@skills_router.get("", response_model=list[SkillOut])
def public_skills(db: Session = Depends(get_db)):
    items = db.scalars(select(Skill).where(Skill.is_visible.is_(True)).order_by(Skill.category, Skill.sort_order, Skill.id)).all()
    return [_skill_payload(item) for item in items]


@admin_router.get("", response_model=list[CareerOut])
def admin_career(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return [_career_payload(item) for item in db.scalars(select(CareerEntry).order_by(CareerEntry.sort_order, CareerEntry.id)).all()]


@admin_router.post("", response_model=CareerOut, status_code=201)
def create_career(data: CareerCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = CareerEntry()
    _apply_career(item, data.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return _career_payload(item)


@admin_router.patch("/{item_id}", response_model=CareerOut)
def update_career(item_id: int, data: CareerUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.get(CareerEntry, item_id)
    if not item: raise HTTPException(status_code=404, detail="المحطة غير موجودة")
    _apply_career(item, data.model_dump(exclude_unset=True))
    db.commit(); db.refresh(item)
    return _career_payload(item)


@admin_skills_router.get("", response_model=list[SkillOut])
def admin_skills(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return [_skill_payload(item) for item in db.scalars(select(Skill).order_by(Skill.category, Skill.sort_order, Skill.id)).all()]


@admin_skills_router.post("", response_model=SkillOut, status_code=201)
def create_skill(data: SkillCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = Skill(); _apply_skill(item, data.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return _skill_payload(item)


@admin_skills_router.patch("/{item_id}", response_model=SkillOut)
def update_skill(item_id: int, data: SkillUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.get(Skill, item_id)
    if not item: raise HTTPException(status_code=404, detail="المهارة غير موجودة")
    _apply_skill(item, data.model_dump(exclude_unset=True))
    db.commit(); db.refresh(item)
    return _skill_payload(item)


@admin_skills_router.delete("/{item_id}", status_code=204)
def delete_skill(item_id: int, confirm: bool = False, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    if not confirm: raise HTTPException(status_code=400, detail="يتطلب الحذف تأكيداً صريحاً")
    item = db.get(Skill, item_id)
    if not item: raise HTTPException(status_code=404, detail="المهارة غير موجودة")
    db.delete(item); db.commit()
