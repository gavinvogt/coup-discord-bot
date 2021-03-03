# Running the bot
Create a `.env` file (see below section) in the same directory as `launcher.py`.
Run `launcher.py` and use command prefix `c!`


# env file format
DISCORD_TOKEN="{YOUR-TOKEN-HERE}"


# Writing the bot
The code quickly got messy as I progressively realized the variety in ways I would have to deal with
various possible game states in Coup. Just look at `classes/coup_game.py` for an example of the
confusion that ensued. I added methods haphazardly, and as a result the code was much less elegant
and clean. It quickly became more time-effective to just put all the code for each method within
that method's body instead of scrolling to the bottom, adding a "private" method, and finding the
method I was writing in the first place to complete the method. The number of lines of code in some
methods is rather frightening. I also may have gotten overexcited with abstract base classes,
inheritance, and properties, but that's an entire different discussion.

Overall, though, I am happy with how the bot turned out. It's satisfying to see the generally-written
code be able to handle specific cases properly (particularly through my use of the `cog_after_invoke()`
method in `cogs/game_cog.py` and the command checks I wrote in `helpers/command_checks.py`).

# What I would improve
If I had to rewrite the bot, I would make a separate class representing the `CardPile` and store it
as a field in `CoupGame`, since I had a multitude of methods that just referred to the card pile. I
would also store the turn order in another class to make it easier to deal with the turn order and
whose turn is whose.
