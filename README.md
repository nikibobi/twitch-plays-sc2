# Twitch plays StarCraft 2
Before starting the bot create a file `.secrets` in the same folder as the bot with content:

`<username> <client_id> <token> <channel>`

Start bot with:

`python -m pysc2.bin.agent --map <map> --agent chatbot.TwitchAgent --agent_race <race> --bot_race <race> --difficulty <1-9> --step_mul 1 --max_agent_steps 0`

Example:

`python -m pysc2.bin.agent --map Acolyte --agent chatbot.TwitchAgent --agent_race Z --bot_race R --difficulty 1 --step_mul 1 --max_agent_steps 0`
