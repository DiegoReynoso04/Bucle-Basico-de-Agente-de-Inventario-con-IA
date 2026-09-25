"""Modelos de producto y sus validaciones."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, computed_field

# Los espacios exteriores se eliminan antes de comprobar la longitud,
# de modo que "   " se rechaza como nombre vacío.
ProductName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Unit = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]
# strict: rechaza booleanos, decimales y cadenas numéricas en lugar de convertirlos.
NonNegativeInt = Annotated[int, Field(ge=0, strict=True)]


def name_key(name: str) -> str:
    """Clave de identidad de un producto: sin espacios exteriores y sin distinguir mayúsculas."""
    return name.strip().casefold()


class ProductCreate(BaseModel):
    """Datos necesarios para registrar un producto."""

    model_config = ConfigDict(frozen=True)

    name: ProductName
    quantity: NonNegativeInt
    unit: Unit
    min_stock: NonNegativeInt


class Product(ProductCreate):
    """Producto del inventario. `low_stock` se calcula y no se almacena."""

    @computed_field
    @property
    def low_stock(self) -> bool:
        return self.quantity <= self.min_stock
