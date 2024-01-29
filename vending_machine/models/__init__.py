from pydantic import BaseModel, validator


class BasePydantic(BaseModel):
    """
    Base class for all Pydantic models.

    This class is used to add the `is_orm` and `orm_model` attributes to all Pydantic models.

    `is_orm` is a boolean that indicates whether the model is an ORM model or not.  Assume False, unless overridden.

    `orm_model` is the ORM model that corresponds to the Pydantic model.  If `is_orm` is False, this should be None.
    """

    is_orm: bool = False
    orm_model: object | None = None

    @validator("orm_model", always=True)
    def orm_model_must_be_none_if_not_is_orm(
        cls, v: object | None, values: dict[str, object]
    ) -> object | None:
        if values.get("is_orm") is True and values.get("orm_model") is None:
            raise ValueError("orm_model must be set if is_orm is True")

        return v
