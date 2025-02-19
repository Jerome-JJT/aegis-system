install Debian GNU/Linux 12 (bookworm)  (/etc/os-release)

#### Github

`ssh-keygen`<br>
`deploy key w/ edit`<br>
`git clone project`<br>
`python -m venv env`<br>
`source env/bin/activate`<br>
`pip install -r requirements.txt`<br>
`pip install Adafruit_Python_DHT --install-option="--force-pi"`<br>
`.env`<br>
`.aegis_config`<br>

#### Wifi prod
`sudo nmcli dev wifi rescan`<br>
`sudo nmcli dev wifi list`<br>
<br>
`cd /etc/NetworkManager/system-connections`<br>
`ll`

#### Sets
`sudo apt update`<br>
`sudo apt upgrade`<br>
~~`sudo apt install midori`~~<br>
~~`wget http://ftp.fr.debian.org/debian/pool/main/m/midori/midori_7.0-2.1_armhf.deb`~~<br>
~~`sudo dpkg -i midori_XXXXX.deb`~~<br>
~~`sudo apt -f install`~~<br>
`sudo apt install epiphany-browser`<br>
`crontab -e`<br>
Add `*/5 * * * *  cd /home/admin/aegis-system; ./env/bin/python ./code/_common/discord_message.py "$(date) $(hostname -I) $(iwgetid)"`<br>
`sudo nano /etc/rc.local`<br>
Add `cd /home/admin/aegis-system; ./env/bin/python ./code/_common/discord_message.py "STARTUP $(date) $(hostname -I) $(iwgetid)"`<br>


#### Services
`sudo mkdir -p /var/log/aegis`<br>
`sudo chown -R admin:admin /var/log/aegis`<br>
`mkdir -p ~/.config/systemd`<br>
`ln -s ~/aegis-system/services ~/.config/systemd/user`<br>
`visudo`<br>
Add `admin ALL=(ALL) NOPASSWD: /home/admin/aegis-system/services/manage_hdmi.sh`<br>

`systemctl --user enable server`<br>
`systemctl --user enable watcher`<br>
`systemctl --user enable nginx`<br>
`systemctl --user enable browser`<br>


#### Reconnect wifi auto
`https://raspberrypi.stackexchange.com/questions/71626/automatically-connect-pi-zero-w-to-wlan-after-lost-connection`<br>
As root <br>
```sh
#!/bin/bash

# The IP for the server you wish to ping. I suggest an internal gateway.
SERVER=192.168.1.1

# Only send two pings, sending output to /dev/null
ping -c2 ${SERVER} > /dev/null
echo "Run $(date)"

# If the return code from ping ($?) is not 0 (meaning there was an error)
if [ $? != 0 ]
then
    echo "Restart wlan0"
    # Restart the wireless interface
    ip link set wlan0 down
    sleep 1
    ip link set wlan0 up
fi
```
<br>
/etc/crontab `*/5 * * * * /root/wifi_rebooter.sh >> /root/log.txt 2>> /root/log.txt`<br>

