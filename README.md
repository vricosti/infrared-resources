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