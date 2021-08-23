SERVICE="mono"
if pgrep -x "$SERVCE" >/dev/null
then
	echo "$SERVICE is running"
else
	cd /home/pi/terraria
	screen -dmS terraria mono TerrariaServer.exe -players 3 -world /mnt/slowhdd/terraria/The_Lonely_Alan.wld

fi
