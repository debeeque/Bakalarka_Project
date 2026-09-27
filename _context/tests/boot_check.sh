b=$(date -d "$(uptime -s)" +%s)
x=$(date -d "$(ps -o lstart= -p $(pgrep -x Xorg | head -1))" +%s 2>/dev/null || echo 0)
g=$(date -d "$(ps -o lstart= -p $(pgrep -f '^python3 gui_app.py' | head -1))" +%s 2>/dev/null || echo 0)
m=$(sudo ip -n analyzer_monitor -br link show mon0 2>/dev/null | awk '{print $3}')
s=$(sudo ip -n analyzer_sender -br link show snd0 2>/dev/null | awk '{print $3}')
ok=FAIL; [ "$m" = "00:e0:4c:68:02:01" ] && [ "$s" = "00:e0:4c:68:02:23" ] && ok=OK
u=$(systemctl show -p Result --value analyzer-port@mon0)/$(systemctl show -p Result --value analyzer-port@snd0)
t=$(journalctl -b --no-pager | grep -c "sudo\[.*TTY=tty1")
echo "$(uptime -s),$((x-b)),$((g-b)),${m:-none},${s:-none},$ok,$u,$t"
