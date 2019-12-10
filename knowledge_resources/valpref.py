from dataclasses import dataclass, field


@dataclass
class ValPref:
    values: list[str] = field(default=[])

    def remove_value(self, old_value: str):
        self.values.remove(old_value)

    def get_preferred(self):
        try:
            return self.values[0]
        except IndexError:
            return None
