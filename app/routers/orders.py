from fastapi import APIRouter, HTTPException
from app.models import Order, Item
from app.schemas.order_item import OrderCreate, OrderResponse
from app.dependencies import db_dep, current_user_dep

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=list[OrderResponse])
def list_orders(
    db: db_dep,
    current_user: current_user_dep
):
    if current_user.is_superuser:
        return db.query(Order).all()
    return db.query(Order).filter(Order.customer_id == current_user.id).all()


@router.post("/", response_model=OrderResponse)
def create_order(
    data: OrderCreate,
    db: db_dep,
    current_user: current_user_dep
):
    item = db.query(Item).get(data.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    order = Order(
        customer_id=current_user.id,
        restaurant_id=data.restaurant_id,
        delivery_address=data.delivery_address,
        total_cents=data.total_cents,
        status=data.status,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}/", response_model=dict)
def delete_order(
    order_id: int,
    db: db_dep,
    current_user: current_user_dep
):
    order = db.query(Order).get(order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.customer_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(order)
    db.commit()
    return {"detail": "Order deleted"}
