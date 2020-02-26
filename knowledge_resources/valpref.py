from dataclasses import dataclass, field
from typing import List


@dataclass
class ValPref:
    values: List[str] = field(default_factory=lambda:[])

    def remove_value(self, old_value: str):
        self.values.remove(old_value)

    def add_value(self, new_value: str):
        self.values.append(new_value)

    def get_preferred(self):
        try:
            return self.values[0]
        except IndexError:
            return None
