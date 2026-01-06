from enum import Enum


class ProductTypes(Enum):
    """
    Enumeration of available product categories.

    Attributes
    ----------
    DRINK : str
        Beverage products (e.g., sodas, water, juices)
    SNACK : str
        Snack products (e.g., chips, candy, nuts)
    FOOD : str
        Food products (e.g., sandwiches, meals)
    """

    DRINK = "drink"
    SNACK = "snack"
