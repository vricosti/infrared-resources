# infrared-resources

Deprecated method based on lirc:  

```
sudo apt install lirc
sudo mv /etc/lirc/lircd.conf.d/devinput.lircd.conf /etc/lirc/lircd.conf.d/devinput.lircd.conf.dist
```

sudo vim /boot/config.txt:
```
# Uncomment this to enable infrared communication.
dtoverlay=gpio-ir,gpio_pin=18
dtoverlay=gpio-ir-tx,gpio_pin=17
```


sudo vim /etc/lirc/lirc_options.conf

To use as a  ir receiver
```
driver          = default
device          = /dev/lirc1
```
and for a ir transmitter:

```
driver          = default
device          = /dev/lirc0
```
Now to test receiver:

```
sudo systemctl stop lircd
mode2 -d /dev/lirc1
```

https://github.com/raspberrypi/linux/issues/2993  
Add these rules in /etc/udev/rules.d/71-lirc.rules to get stable /dev/lirc-rx and /dev/lirc-tx device names:

Instead of the use of confusing lirc0, lirc1 we define some aliases:  

```
ACTION=="add", SUBSYSTEM=="lirc", DRIVERS=="gpio_ir_recv", SYMLINK+="lirc-rx"  
ACTION=="add", SUBSYSTEM=="lirc", DRIVERS=="gpio-ir-tx", SYMLINK+="lirc-tx"  
```


Record keys with ir-keytable (that is completely broken if you want my opinion):  
`ir-keytable -t -s rc0`  
  
Record keys with ir-ctl as raw codes:  
`ir-ctl -d /dev/lirc1 -r > SONY-KEY_POWER.txt`  
  
Send a key using a file containing raw data:  
`ir-ctl -v -d /dev/lirc-tx --send=SONY-KEY_POWER.txt' with data like +2400 -600 +1200 -600 +600 -600 +1200 -600 ... `  
  
Send a key using a toml file:  
`ir-ctl -v -d /dev/lirc-tx -k sony-raw.toml -K KEY_POWER`  


