class Nutrient:
    def __init__(self, data):
        try:
            self.calories = data["Calories / 100g"]
            self.protein = data["Protéine"]
            self.fat = data["Fat"]
            self.sfat = data["SFat"]
            self.carbs = data["Carbs"]
            self.sugar = data["Sugar"]
            self.free_sugar = data["Free sugar"]
            self.fibres = data["Fibres"]
            self.salt = data["Sel"]
            self.alcohol = data["Alcool"]
            self.water = data["Water"]
            # Sodium is derived from salt (Sel). 1g of salt = 400mg of sodium.
            self.sodium = self.salt * 400
        except KeyError as e:
            raise ValueError(f"Missing nutrient data: {e}")
        self.missing_foods = []  # Track missing foods that used default values

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            new_data = {
                "Calories / 100g": self.calories * other,
                "Protéine": self.protein * other,
                "Fat": self.fat * other,
                "SFat": self.sfat * other,
                "Carbs": self.carbs * other,
                "Sugar": self.sugar * other,
                "Free sugar": self.free_sugar * other,
                "Fibres": self.fibres * other,
                "Sel": self.salt * other,
                "Alcool": self.alcohol * other,
                "Water": self.water * other,
            }
            return Nutrient(new_data)
        elif isinstance(other, Nutrient):
            # Multiplication of two Nutrient objects is not supported in this context.
            # It likely indicates a malformed formula (e.g., "food1 * food2").
            # Returning NotImplemented will cause a TypeError, which is appropriate.
            return NotImplemented
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        if isinstance(other, Nutrient):
            new_data = {
                "Calories / 100g": self.calories + other.calories,
                "Protéine": self.protein + other.protein,
                "Fat": self.fat + other.fat,
                "SFat": self.sfat + other.sfat,
                "Carbs": self.carbs + other.carbs,
                "Sugar": self.sugar + other.sugar,
                "Free sugar": self.free_sugar + other.free_sugar,
                "Fibres": self.fibres + other.fibres,
                "Sel": self.salt + other.salt,
                "Alcool": self.alcohol + other.alcohol,
                "Water": self.water + other.water,
            }
            new_nutrient = Nutrient(new_data)
            new_nutrient.sodium = self.sodium + other.sodium
            return new_nutrient
        elif isinstance(other, (int, float)):
            # When adding a float, assume it's an adjustment to calories
            new_data = self.to_dict()  # Start with current values
            new_data["Calories / 100g"] = self.calories + other
            return Nutrient(new_data)
        return NotImplemented

    def __radd__(self, other):
        # Handle right-hand side addition (float + Nutrient)
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Nutrient):
            new_data = {
                "Calories / 100g": self.calories - other.calories,
                "Protéine": self.protein - other.protein,
                "Fat": self.fat - other.fat,
                "SFat": self.sfat - other.sfat,
                "Carbs": self.carbs - other.carbs,
                "Sugar": self.sugar - other.sugar,
                "Free sugar": self.free_sugar - other.free_sugar,
                "Fibres": self.fibres - other.fibres,
                "Sel": self.salt - other.salt,
                "Alcool": self.alcohol - other.alcohol,
                "Water": self.water - other.water,
            }
            new_nutrient = Nutrient(new_data)
            new_nutrient.sodium = self.sodium - other.sodium
            return new_nutrient
        elif isinstance(other, (int, float)):
            # When subtracting a float, assume it's an adjustment to calories
            new_data = self.to_dict()  # Start with current values
            new_data["Calories / 100g"] = self.calories - other
            return Nutrient(new_data)
        return NotImplemented

    def __rsub__(self, other):
        # Handle right-hand side subtraction (float - Nutrient)
        if isinstance(other, (int, float)):
            # This is less common, but if it happens, it means 'float - Nutrient'
            # We'll assume it means 'float - Nutrient.calories' and other nutrients are negative
            new_data = self.to_dict()
            new_data["Calories / 100g"] = other - self.calories
            # For other nutrients, it's ambiguous, so we'll make them negative
            for key in new_data:
                if key != "Calories / 100g":
                    new_data[key] = -new_data[key]
            return Nutrient(new_data)
        return NotImplemented

    def __truediv__(self, scalar):
        if isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ZeroDivisionError("Cannot divide Nutrient by zero")
            return self * (1 / scalar)
        return NotImplemented

    def __rtruediv__(self, other):
        # Division of a float by a Nutrient object is ambiguous in this context.
        # It's better to explicitly not support it unless a clear interpretation is defined.
        return NotImplemented

    def __repr__(self):
        return f"Nutrient(cal={self.calories}, prot={self.protein}, fat={self.fat}, sodium={self.sodium})"

    def to_dict(self):
        return {
            "calories": self.calories,
            "protein": self.protein,
            "fat": self.fat,
            "sfat": self.sfat,
            "carbs": self.carbs,
            "sugar": self.sugar,
            "free_sugar": self.free_sugar,
            "fibres": self.fibres,
            "salt": self.salt,
            "alcohol": self.alcohol,
            "water": self.water,
            "sodium": self.sodium,
        }
