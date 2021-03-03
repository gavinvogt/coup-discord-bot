'''
File: info_cog.py
Author: Gavin Vogt
This program defines the Info cog for the Coup bot
'''

# dependencies
from discord.ext import commands
from discord import User, Embed, Color

# my code
from cogs.base_cog import BaseCog
from classes.coup_game import CoupGame
from helpers.command_checks import channel_has_game, is_player, game_is_started

# Define help strings
SETTINGS_HELP = "Show game settings"
COINS_HELP = "Checks how many coins you or another player have"
HAND_HELP = "Shows information about your or another player's hand"
TURN_HELP = "Check whose turn it is"
DEAD_HELP = "Shows pile of dead cards"
SUMMARY_HELP = "Shows game summary"
PENDING_HELP = "Shows what actions the game is waiting on"
RULES_HELP = "Game rules"
GUIDE_HELP = "Gameplay commands guide"
COUNT_HELP = "Shows player count"
DN_HELP = "Find out for yourself"


class InfoCog(BaseCog, name="info"):
    '''
    Commands for getting various information about the current game
    '''
    def __init__(self, bot):
        super().__init__(bot)

    @commands.command(name="settings", help=SETTINGS_HELP)
    @channel_has_game()
    @commands.guild_only()
    async def send_game_settings(self, ctx):
        '''
        Sends the embed representing the game settings
        '''
        game = self.bot.get_game(ctx.channel.id)
        await ctx.send(embed=game.setup_embed(ctx.channel.mention))

    @commands.command(name="rules", help=RULES_HELP)
    async def send_rules(self, ctx):
        '''
        Sends the embed representing the game rules
        '''
        await ctx.send(embed=CoupGame.rules_embed(self.bot.command_prefix))

    @commands.command(name="guide", help=GUIDE_HELP)
    async def send_guide(self, ctx):
        '''
        Sends the embed giving the guide
        '''
        # Set up action / response information
        prefix = self.bot.command_prefix
        actions = (
            (f"`{prefix}assassinate`", "`Assassin`", "`Assassinate a player for 3 coins`"),
            (f"`{prefix}steal`", "`Captain`", "`Steal 2 coins from a player`"),
            (f"`{prefix}exchange`", "`Ambassador`", "`Look at 2 cards in pile and swap`"),
            (f"`{prefix}tax`", "`Duke`", "`Take 3 coins`"),
            (f"`{prefix}income`", "`ANY`", "`Take 1 coin`"),
            (f"`{prefix}foreignaid`", "`ANY`", "`Take 2 coins`"),
            (f"`{prefix}coup`", "`ANY`", "`Coup a player for 7 coins`"),
        )
        responses = (
            (f"`{prefix}block contessa`", "`Contessa`", "`Block an assassination`"),
            (f"`{prefix}block doublecontessa`", "`Double Contessa`", "`Block a coup`"),
            (f"`{prefix}block captain`", "`Captain`", "`Block a steal`"),
            (f"`{prefix}block ambassador`", "`Ambassador`", "`Block a steal`"),
            (f"`{prefix}block duke`", "`Duke`", "`Block foreign aid`"),
            (f"`{prefix}pass`", "`ANY`", "`Allow action to occur`"),
            (f"`{prefix}die`", "`ANY`", "`Select which card(s) to die`"),
            (f"`{prefix}challenge`", "`ANY`", "`Challenge an action`"),
        )

        guide_embed = Embed(
            title = "Gameplay Guide",
            color = Color.orange(),
        )

        guide_embed.add_field(name="Actions", value="\n".join(info[0] for info in actions))
        guide_embed.add_field(name="Influences", value="\n".join(info[1] for info in actions))
        guide_embed.add_field(name="Descriptions", value="\n".join(info[2] for info in actions))

        guide_embed.add_field(name="Responses", value="\n".join(info[0] for info in responses))
        guide_embed.add_field(name="Influences", value="\n".join(info[1] for info in responses))
        guide_embed.add_field(name="Descriptions", value="\n".join(info[2] for info in responses))

        guide_embed.set_footer(text=f"See {prefix}rules for game rules")
        await ctx.send(embed=guide_embed)

    @commands.command(name="coins", help=COINS_HELP)
    @game_is_started()
    @is_player()
    @channel_has_game()
    @commands.guild_only()
    async def send_coin_count(self, ctx, user: User = None):
        '''
        Shows the player their coin count in the current game
        user: discord.User to show coin count of (optional)
        '''
        game = self.bot.get_game(ctx.channel.id)
        if user is None:
            player = game.get_player(ctx.author.id)
            await ctx.send(f"You have `{player.get_coins()}` coins")
        else:
            player = game.get_player(user.id)
            if player is None:
                await ctx.send(f"{user.mention} is not part of this game")
            else:
                await ctx.send(f"{user.mention} has `{player.get_coins()}` coins")

    @commands.command(name="hand", help=HAND_HELP)
    @game_is_started()
    @is_player()
    @channel_has_game()
    @commands.guild_only()
    async def show_hand(self, ctx, user: User = None):
        '''
        Shows the player their hand in the current game
        user: discord.User to show hand of (optional and only shows revealed cards)
        '''
        # Get the Player profile and send them their hand
        game = self.bot.get_game(ctx.channel.id)

        if user is None:
            player = game.get_player(ctx.author.id)
            await ctx.author.send(embed=player.get_embed(ctx))
        else:
            player = game.get_player(user.id)
            if player is None:
                await ctx.send(f"{user.mention} is not part of this game")
            else:
                await ctx.send(embed=player.get_visible_embed())

    @commands.command(name="turn", help=TURN_HELP)
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def show_turn(self, ctx):
        '''
        Show whos turn it is
        '''
        game = self.bot.get_game(ctx.channel.id)
        await ctx.send(f"It is {game.get_turn().get_mention()}'s turn")

    @commands.command(name="dead", help=DEAD_HELP)
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def show_dead_pile(self, ctx):
        '''
        Shows the pile of dead cards
        '''
        game = self.bot.get_game(ctx.channel.id)
        await ctx.send(embed=game.dead_embed())

    @commands.command(name="pending", help=PENDING_HELP, aliases=['pend'])
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def send_pending_summary(self, ctx):
        '''
        Sends the summary of pending players
        '''
        game = self.bot.get_game(ctx.channel.id)
        await ctx.send(embed=game.pending_players_embed())

    @commands.command(name="summary", help=SUMMARY_HELP, aliases=['sum'])
    @game_is_started()
    @channel_has_game()
    @commands.guild_only()
    async def send_game_summary(self, ctx):
        '''
        Sends the game summary
        '''
        game = self.bot.get_game(ctx.channel.id)
        await ctx.send(embed=game.summary_embed())

    @commands.command(name="count", help=COUNT_HELP)
    @channel_has_game()
    @commands.guild_only()
    async def send_player_count(self, ctx):
        '''
        Sends the player count for the game in this channel
        '''
        game = self.bot.get_game(ctx.channel.id)
        await ctx.send(f"Current player count: `{game.player_count()}`")

    @commands.command(name="dn", help=DN_HELP, hidden=True)
    async def deez_nuts(self, ctx, user: User):
        if ctx.author.id == user.id:
            # tried to use command on self
            await ctx.send("You can't use this command on yourself")
        elif await self.bot.is_owner(user):
            # tried to use command on owner
            await ctx.send(f"Nice try; {user.mention} makes {ctx.author.mention} gargle deez nuts in retribution")
        else:
            await ctx.send(f"{user.mention} gargles deez nuts")


def setup(bot):
    bot.add_cog(InfoCog(bot))