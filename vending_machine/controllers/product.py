from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from vending_machine.authentication import get_buyer_or_seller_user, get_seller_user
from vending_machine.database import get_db
from vending_machine.models.user import UserWithoutPassword
from vending_machine.models.product import Product, ProductCreate

routes = APIRouter()


# Create a product
@routes.post("/products/create", response_model=Product)
async def create_product(
    product: ProductCreate,
    current_user: UserWithoutPassword = Depends(get_seller_user),
    db: AsyncSession = Depends(get_db),
) -> Product:
    try:
        new_product = Product(**product.model_dump())
        new_product.seller_id = current_user.id

        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)

        return Product(new_product)

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())
    except Exception as e:
        if routes.app.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


# Get all Products
@routes.get("/products", response_model=list[Product])
async def get_products(
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> list[Product]:
    try:
        assert isinstance(
            current_user, UserWithoutPassword
        ), "User was not authorised"  # Probably unnecessary defensive coding

        products = await db.query(Product).all()

        return [Product(product) for product in products]
    except AssertionError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except Exception as e:
        if routes.app.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


# Get one Product
@routes.get("/products/{product_id}", response_model=Product)
async def get_product(
    product_id: int,
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> Product:
    try:
        assert isinstance(
            current_user, UserWithoutPassword
        ), "User was not authorised"  # Probably unnecessary defensive coding

        product = await db.query(Product).filter(Product.id == product_id).first()

        return Product(product)
    except AssertionError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except Exception as e:
        if routes.app.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")

# Update a product
@routes.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product: ProductCreate,
    current_user: UserWithoutPassword = Depends(get_seller_user),
    db: AsyncSession = Depends(get_db),
) -> Product:
    try:
        assert isinstance(
            current_user, UserWithoutPassword
        ), "User was not authorised"  # Probably unnecessary defensive coding

        product = await db.query(Product).filter(Product.id == product_id).first()

        if not product or (product.seller_id != current_user.id):
            # We return a 400 here instead of a 404 to prevent leaking information about the existence of products
            # Technically, there's a layer of auth above this, but buyers could fuzz the system
            raise HTTPException(status_code=400, detail="Product retrieval")

        product.update(**product.model_dump())

        await db.commit()
        await db.refresh(product)

        return Product(product)

    except AssertionError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())
    except Exception as e:
        if routes.app.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
        

# Delete a product
@routes.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    current_user: UserWithoutPassword = Depends(get_seller_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        assert isinstance(
            current_user, UserWithoutPassword
        ), "User was not authorised"  # Probably unnecessary defensive coding

        product = await db.query(Product).filter(Product.id == product_id).first()

        if not product or (product.seller_id != current_user.id):
            # We return a 400 here instead of a 404 to prevent leaking information about the existence of products
            # Technically, there's a layer of auth above this, but buyers could fuzz the system
            raise HTTPException(status_code=400, detail="Product retrieval")

        db.delete(product)
        await db.commit()

    except AssertionError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except Exception as e:
        if routes.app.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")