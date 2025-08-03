from fastapi import APIRouter, HTTPException, Query
from app.models import Item, Restaurant
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse
from app.dependencies import db_dep, current_user_dep

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/", response_model=list[ItemResponse])
def list_items(
    db: db_dep,
    name: str = Query(None),
    restaurant_id: int = Query(None),
    min_price: float = Query(None),
    max_price: float = Query(None),
    skip: int = 0,
    limit: int = 10,
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    query = db.query(Item)

    if name:
        query = query.filter(Item.name.ilike(f"%{name}%"))
    if restaurant_id:
        query = query.filter(Item.restaurant_id == restaurant_id)
    if min_price is not None:
        query = query.filter(Item.price >= min_price)
    if max_price is not None:
        query = query.filter(Item.price <= max_price)

    sort_column = getattr(Item, sort_by, Item.id)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    return query.order_by(sort_column).offset(skip).limit(limit).all()



@router.post("/", response_model=ItemResponse)
def create_item(
    data: ItemCreate,
    db: db_dep,
    current_user: current_user_dep
):
    if not current_user.is_superuser and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    restaurant = db.query(Restaurant).get(data.restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    item = Item(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}/", response_model=ItemResponse)
def update_item(
    item_id: int,
    data: ItemUpdate,
    db: db_dep,
    current_user: current_user_dep
):
    if not current_user.is_superuser and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    item = db.query(Item).get(item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}/", response_model=dict)
def delete_item(
    item_id: int,
    db: db_dep,
    current_user: current_user_dep
):
    if not current_user.is_superuser and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    item = db.query(Item).get(item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"detail": "Item deleted"}