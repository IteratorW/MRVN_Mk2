from tortoise import Model, fields

from api.list_field import ListField


class AiTextModel(Model):
    seed = fields.IntField(pk=True)
    text = fields.TextField()
    temperature = fields.FloatField()

    likes = ListField[int](default=[])
    dislikes = ListField[int](default=[])

    def react(self, user_id: int, like: bool) -> bool:
        if like and user_id in self.dislikes:
            self.dislikes.remove(user_id)
        elif not like and user_id in self.likes:
            self.likes.remove(user_id)

        if like and user_id not in self.likes:
            self.likes.append(user_id)

            return True
        elif not like and user_id not in self.dislikes:
            self.dislikes.append(user_id)

            return True

        return False
