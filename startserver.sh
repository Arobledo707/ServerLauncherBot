SERVICE="mono"
if pgrep -x "$SERVCE" >/dev/null
then
	echo "$SERVICE is running"
else
# enter path to terraria directory replace /home/pi/terraria that is just the directory where I had my TShock terraria files
	cd /home/pi/terraria
	# replace /mnt/slowhdd/terraria/testmap.wld you can customize and of the TerrariaServer.exe flags to how you want to have your server set up.
	screen -dmS terraria mono TerrariaServer.exe -players 3 -world /mnt/slowhdd/terraria/testmap.wld

fi
