from discord import User

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.models import MrvnUser
from api.translation.translatable import Translatable
from impl import runtime

owners_group = runtime.bot.create_group("owners", category=categories.owners_only,
                                        owners_only=True)


@owners_group.command(name="list", description=Translatable("std_command_owner_list"))
async def owner_list(ctx: MrvnCommandContext):
    users = await MrvnUser.filter(is_owner=True)

    if not len(users):
        await ctx.respond_embed(Style.ERROR, ctx.translate("std_command_owners_no_owners"))

        return

    owners = [user.mention if (user := runtime.bot.get_user(x.user_id)) else ctx.translate("std_command_owners_unknown") for x in users]

    await ctx.respond_embed(Style.INFO, ctx.format("std_command_owners_list", "\n".join(owners)))


async def edit_owner(ctx: MrvnCommandContext, user: User, add_: bool):
    mrvn_user = (await MrvnUser.get_or_create(user_id=user.id))[0]

    if add_ and mrvn_user.is_owner:
        await ctx.respond_embed(Style.ERROR, ctx.translate("std_command_owner_already_an_owner"))

        return
    elif not add_ and not mrvn_user.is_owner:
        await ctx.respond_embed(Style.ERROR, ctx.translate("std_command_owner_not_an_owner"))

        return

    mrvn_user.is_owner = add_

    await mrvn_user.save()

    await ctx.respond_embed(Style.OK, ctx.format("std_command_owner_add" if add_ else "std_command_owner_remove", user.mention))


@owners_group.command(description=Translatable("std_command_owner_add_desc"))
async def add(ctx: MrvnCommandContext, user: User):
    await edit_owner(ctx, user, True)


@owners_group.command(description=Translatable("std_command_owner_remove_desc"))
async def remove(ctx: MrvnCommandContext, user: User):
    await edit_owner(ctx, user, False)
