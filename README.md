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

ACTION=="add", SUBSYSTEM=="lirc", DRIVERS=="gpio_ir_recv", SYMLINK+="lirc-rx"
ACTION=="add", SUBSYSTEM=="lirc", DRIVERS=="gpio-ir-tx", SYMLINK+="lirc-tx"
ACTION=="add", SUBSYSTEM=="lirc", DRIVERS=="pwm-ir-tx", SYMLINK+="lirc-tx"

