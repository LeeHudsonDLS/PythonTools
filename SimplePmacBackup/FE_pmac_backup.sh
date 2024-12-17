#!/bin/sh
for i in $(seq 8026 8096); do
    if [ $(lsof -i:$i | wc -m) -gt 0 ]
    then
        echo "Port $i is in use"
    else
        dls-pmac-control.py -o tcpip -s localhost -p $i -n 8 &
        gnome-terminal -e "$(configure-ioc s -p fe-css-wrapper-gui)/scripts/FE_portfwd.sh $1 $2 $i"
        echo "Using port $i"
        break
    fi
done
