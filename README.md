# Running the bot
Create a `.env` file (see below section) in the same directory as `launcher.py`.
Run `launcher.py` and use command prefix `c!`


# env file format
DISCORD_TOKEN="{YOUR-TOKEN-HERE}"


# Writing the bot
The code quickly got messy as I progressively realized the variety in ways I would have to deal with
various possible game states in Coup. Just look at `classes/coup_game.py` for an example of the
confusion that ensued. I also may have gotten overexcited with abstract base classes and inheritance,
but that's an entire different discussion.

Overall, though, I am happy with how the bot turned out. It's satisfying to see the generally-written
code be able to handle specific cases properly (particularly through my use of the `cog_after_invoke()`
method in `game_cog.py` and the command checks I wrote in `helpers/command_checks.py`.
