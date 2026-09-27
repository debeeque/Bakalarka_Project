#!/bin/bash
LOG="C:/Users/Debeeque/AppData/Local/Temp/claude/C--Projects-Bakalarka/5290cb75-0a08-4f6f-8b37-f42101b416db/scratchpad/reboot_series.csv"
echo "run,boot,x_s,gui_s,mon0_mac,snd0_mac,map,port_units,gui_sudo_tty1" > "$LOG"
for i in $(seq 1 10); do
    ssh -o ConnectTimeout=5 malina 'sudo systemctl reboot' >/dev/null 2>&1
    sleep 25
    up=0
    for k in $(seq 1 40); do
        if ssh -o ConnectTimeout=4 -o BatchMode=yes malina true 2>/dev/null; then up=1; break; fi
        sleep 3
    done
    if [ $up -eq 0 ]; then echo "$i,SSH_TIMEOUT" >> "$LOG"; continue; fi
    sleep 25
    line=$(ssh -o ConnectTimeout=5 malina 'bash -s' < "C:/Users/Debeeque/AppData/Local/Temp/claude/C--Projects-Bakalarka/5290cb75-0a08-4f6f-8b37-f42101b416db/scratchpad/boot_check.sh" 2>&1 | tail -1)
    echo "$i,$line" >> "$LOG"
done
echo DONE >> "$LOG"
