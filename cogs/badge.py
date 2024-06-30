"""
Unifier - A sophisticated Discord bot uniting servers and platforms
Copyright (C) 2024  Green, ItsAsheer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import nextcord
from nextcord.ext import commands
from utils import log, restrictions as r
from enum import Enum
from utils import langmgr

restrictions = r.Restrictions()

class UserRole(Enum):
    OWNER = langmgr.get("badge.role.owner","the instance\'s **owner**")
    ADMIN = langmgr.get("badge.role.admin","the instance\'s **admin**")
    MODERATOR = langmgr.get("badge.role.moderator","the instance\'s **moderator**")
    TRUSTED =langmgr.get("badge.role.verified", "a **verified user**")
    BANNED = langmgr.get("badge.role.banned","**BANNED**")
    USER = langmgr.get("badge.role.user","a **user**")

class Badge(commands.Cog, name=':medal: Badge'):
    """Badge contains commands that show you your role in Unifier.

    Developed by Green and ItsAsheer"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = log.buildlogger(self.bot.package, 'badge', self.bot.loglevel)
        self.embed_colors = {
            UserRole.OWNER: (
                self.bot.colors.greens_hair if self.bot.user.id==1187093090415149056 else self.bot.colors.unifier
            ),
            UserRole.ADMIN: nextcord.Color.green(),
            UserRole.MODERATOR: nextcord.Color.purple(),
            UserRole.TRUSTED: self.bot.colors.gold,
            UserRole.BANNED: nextcord.Color.red(),
            UserRole.USER: nextcord.Color.blurple()
        }
        restrictions.attach_bot(self.bot)

    @commands.command()
    async def badge(self, ctx, *, user=None):
        """Shows your Unifier user badge."""
        if user:
            try:
                user = self.bot.get_user(int(user.replace('<@','',1).replace('>','',1).replace('!','',1)))
            except:
                user = ctx.author
        else:
            user = ctx.author
        user_role = self.get_user_role(user.id)
        embed = nextcord.Embed(
            description=f"<@{user.id}> is {user_role.value}.",
            color=self.embed_colors[user_role]
        )
        embed.set_author(
            name=f'@{user.name}',
            icon_url=user.avatar.url if user.avatar else None
        )
        if user_role==UserRole.BANNED:
            embed.set_footer(text=langmgr.get("badge.role.banned.footer",'L bozo'))

        await ctx.send(embed=embed)

    @commands.command(hidden=True,aliases=['trust'],description=langmgr.get("badge.cdm.verify.desc", 'Verifies a user.'))
    @restrictions.admin()
    async def verify(self, ctx, action, user: nextcord.User):
        action = action.lower()
        if action not in ['add', 'remove']:
            return await ctx.send(langmgr.get("badge.cmd.verify.invalid_action", "Invalid action. Please use 'add' or 'remove'."))

        if action == 'add':
            if user.id not in self.bot.trusted_group:
                self.bot.trusted_group.append(user.id)
        elif action == 'remove':
            if user.id in self.bot.trusted_group:
                self.bot.trusted_group.remove(user.id)

        self.bot.db['trusted'] = self.bot.trusted_group
        await self.bot.loop.run_in_executor(None, lambda: self.bot.db.save_data())

        user_role = UserRole.TRUSTED if action == 'add' else UserRole.USER
        embed = nextcord.Embed(
            title="Unifier",
            description=f"{'Added' if action == 'add' else 'Removed'} user {user.mention} from the trust group.",
            color=self.embed_colors[user_role],
        )
        await ctx.send(embed=embed)

    def get_user_role(self, user_id):
        if user_id == self.bot.config['owner']:
            return UserRole.OWNER
        elif user_id in self.bot.admins:
            return UserRole.ADMIN
        elif user_id in self.bot.moderators:
            return UserRole.MODERATOR
        elif user_id in self.bot.trusted_group:
            return UserRole.TRUSTED
        elif str(user_id) in self.bot.db['banned']:
            return UserRole.BANNED
        else:
            return UserRole.USER

def setup(bot):
    bot.add_cog(Badge(bot))
