from typing import Union, Type, TypeVar, Generic

from tortoise import Model
from tortoise.fields import TextField

T = TypeVar("T")


class ListField(Generic[T], TextField):
    def get_generic_type(self):
        return self.__orig_class__.__args__[0]

    def to_db_value(self, value: list[T], instance: "Union[Type[Model], Model]") -> str:
        return ";".join([str(x) for x in value])

    def to_python_value(self, value: str) -> list[T]:
        if value.strip() == "":
            return []

        list_type = self.get_generic_type()

        return value.split(";") if list_type == str else [list_type(x) for x in value.split(";")]
