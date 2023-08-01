from tortoise import Model, fields


class MrvnUser(Model):
    user_id = fields.IntField(pk=True)
    is_owner = fields.BooleanField(default=False)
