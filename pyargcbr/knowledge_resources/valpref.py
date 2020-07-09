from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class ValPref:
    """Implementation of the concept ValPref"""
    values: List[str] = field(default_factory=lambda: [])

    def remove_value(self, old_value: str):
        """Removes a value from the values list (values)

        Args:
            old_value (str): The values that will be removed
        """
        self.values.remove(old_value)

    def add_value(self, new_value: str):
        """Adds a value to the values list (values)

        Args:
            new_value (str): The values that will be added
        """
        self.values.append(new_value)

    def get_preferred(self) -> Union[str, None]:
        """Gets the preferred value from the values list (values)

        Returns:
            str, None: The first value of the list
        """
        try:
            return self.values[0]
        except IndexError:
            return None
