from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from vending_machine.authentication import get_buyer_or_seller_user, get_seller_user
from vending_machine.config import settings
from vending_machine.database import get_db
from vending_machine.logging import get_logger
from vending_machine.models.api_messages import ApiMessage
from vending_machine.models.product import Product, ProductCreate
from vending_machine.models.user import UserWithoutPassword

routes = APIRouter()

logger = get_logger(__name__)


# Create a product
@routes.post("/products/create", response_model=Product, tags=["products"])
async def create_product(
    product: ProductCreate,
    current_user: UserWithoutPassword = Depends(get_seller_user),
    db: AsyncSession = Depends(get_db),
) -> Product:
    """
    Create a product in the vending machine.

    Args:
        product (ProductCreate): The product data.

    Returns:
        Product: The created product.

    Raises:
        HTTPException: If the user is not authorized or if there is an internal server error.
        ValidationError: If there are validation errors in the product data.
    """
    try:
        new_product = Product(**product.model_dump())
        new_product.seller_id = current_user.id

        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)

        return Product(new_product)

    except ValidationError as e:
        logger.info(e)
        raise HTTPException(status_code=400, detail=e.errors())
    except Exception as e:
        logger.error(e)
        if settings.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


# Get all Products
@routes.get("/products", response_model=list[Product], tags=["products"])
async def get_products(
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> list[Product]:
    """
    Retrieve a list of products from the database.

    Args:
        current_user (UserWithoutPassword): The current user making the request.

    Returns:
        list[Product]: A list of Product objects retrieved from the database.

    Raises:
        HTTPException: If the user is not authorized or if there is an internal server error.
    """

    try:
        assert isinstance(current_user, UserWithoutPassword), "User was not authorised"

        products = await db.query(Product).all()

        return [Product(product) for product in products]
    except AssertionError as e:
        logger.info(e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except Exception as e:
        logger.error(e)
        if settings.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


# Get one Product
@routes.get("/products/{product_id}", response_model=Product, tags=["products"])
async def get_product(
    product_id: int,
    current_user: UserWithoutPassword = Depends(get_buyer_or_seller_user),
    db: AsyncSession = Depends(get_db),
) -> Product:
    """
    Retrieve a product by its ID.

    Args:
        product_id (int): The ID of the product to retrieve.

    Returns:
        Product: The retrieved product.

    Raises:
        HTTPException: If the user is not authorized or if there is an internal server error.
    """
    try:
        assert isinstance(current_user, UserWithoutPassword), "User was not authorised"

        product = await db.query(Product).filter(Product.id == product_id).first()

        return Product(product)
    except AssertionError as e:
        logger.info(e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    except Exception as e:
        logger.error(e)
        if settings.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


# Update a product
@routes.put("/products/{product_id}", response_model=Product, tags=["products"])
async def update_product(
    product_id: int,
    product: ProductCreate,
    current_user: UserWithoutPassword = Depends(get_seller_user),
    db: AsyncSession = Depends(get_db),
) -> Product:
    """
    Update a product in the vending machine.

    Args:
        product_id (int): The ID of the product to be updated.
        product (ProductCreate): The updated product data.

    Returns:
        Product: The updated product.

    Raises:
        HTTPException: If the user is not authorized, the product does not exist, or there is a server error.
        ValidationError: If there are validation errors in the updated product data.
    """
    try:
        assert isinstance(current_user, UserWithoutPassword), "User was not authorised"

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
        if settings.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


# Delete a product
@routes.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    current_user: UserWithoutPassword = Depends(get_seller_user),
    db: AsyncSession = Depends(get_db),
) -> ApiMessage:
    """
    Delete a product from the vending machine.

    Args:
        product_id (int): The ID of the product to be deleted.

    Returns:
        ApiMessage: A message indicating the success of the deletion.

    Raises:
        HTTPException: If the user is not authorized, the product does not exist, or there is a server error.
    """
    try:
        assert isinstance(current_user, UserWithoutPassword), "User was not authorised"

        product = await db.query(Product).filter(Product.id == product_id).first()

        if not product or (product.seller_id != current_user.id):
            # We return a 400 here instead of a 404 to prevent leaking information about the existence of products
            # Technically, there's a layer of auth above this, but buyers could fuzz the system
            raise HTTPException(status_code=400, detail="Product retrieval")

        db.delete(product)
        await db.commit()

        return ApiMessage(message="Product deleted", success=True)

    except HTTPException as e:
        raise e
    except AssertionError as e:
        raise HTTPException(status_code=403, detail=f"Internal server error: {str(e)}")
    except Exception as e:
        if settings.debug:
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
