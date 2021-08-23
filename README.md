# ServerLauncherBot
Requirements:  
Python 3  
Modules: discord  
Terraria server(I use the TShock repository for my server)  
Admin privledges on a discord server  

This is a Discord bot that is used to launch a terraria server that is running on the same server that the bot is on.
This is used to allow friends in the same server to have control when the server goes up.

Run DiscordServer.py to create the initial config file  
Enter your discord bot's token and the path to your startserver.sh and exitserver.sh files  
Add the roles that you want your bot to listen to aka "Admin", "Moderator" and setup the prefixes  
Example for using the prefix is $ip - this command would get the server's ip if you have a role that can control the bot  
Finally edit the startserver.sh with the correct path of your terraria directory along with the map you would like to play and server settings
