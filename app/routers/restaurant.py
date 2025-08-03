from fastapi import APIRouter, HTTPException, Query, Depends
from app.models import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate, RestaurantResponse
from app.dependencies import db_dep, current_user_dep

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("/", response_model=list[RestaurantResponse])
def list_restaurants(
    db: db_dep,
    name: str = Query(None),
    skip: int = 0,
    limit: int = 10,
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    query = db.query(Restaurant)
    if name:
        query = query.filter(Restaurant.name.ilike(f"%{name}%"))

    sort_column = getattr(Restaurant, sort_by, Restaurant.id)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    return query.order_by(sort_column).offset(skip).limit(limit).all()



@router.post("/", response_model=RestaurantResponse)
def create_restaurant(
    data: RestaurantCreate,
    db: db_dep,
    current_user: current_user_dep
):
    if not current_user.is_superuser and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    restaurant = Restaurant(**data.model_dump())
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.put("/{restaurant_id}/", response_model=RestaurantResponse)
def update_restaurant(
    restaurant_id: int,
    data: RestaurantUpdate,
    db: db_dep,
    current_user: current_user_dep
):
    if not current_user.is_superuser and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    restaurant = db.query(Restaurant).get(restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(restaurant, field, value)

    db.commit()
    db.refresh(restaurant)
    return restaurant


@router.delete("/{restaurant_id}/", response_model=dict)
def delete_restaurant(
    restaurant_id: int,
    db: db_dep,
    current_user: current_user_dep
):
    if not current_user.is_superuser and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    restaurant = db.query(Restaurant).get(restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    db.delete(restaurant)
    db.commit()
    return {"detail": "Restaurant deleted"}