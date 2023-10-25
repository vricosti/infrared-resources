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


### Record keys with ir-keytable (that is completely broken if you want my opinion):  

First we need to find on which sys device our received is plugged:  

`pi@raspberrypi:~/Dev/$ sudo ir-keytable`  

```
Found /sys/class/rc/rc3/ with:
	...
Found /sys/class/rc/rc1/ with:
	Name: gpio_ir_recv
	Driver: gpio_ir_recv
	Default keymap: rc-rc6-mce
	Input device: /dev/input/event4
	LIRC device: /dev/lirc1
	Attached BPF protocols: 
	Supported kernel protocols: lirc rc-5 rc-5-sz jvc sony nec sanyo mce_kbd rc-6 sharp xmp imon 
	Enabled kernel protocols: lirc rc-6 
	bus: 25, vendor/product: 0001:0001, version: 0x0100
	Repeat delay = 500 ms, repeat period = 125 ms
Found /sys/class/rc/rc2/ with:
	...
```

Here we can see that it's mapped to rc1 and the enabled protocols are lirc and rc-6.
So we need to enable all supported protocols:  

`pi@raspberrypi:~/Dev/$ sudo ir-keytable -p all`  

Protocols changed to unknown other lirc rc-5 rc-5-sz jvc sony nec sanyo mce_kbd rc-6 sharp xmp cec imon rc-mm 
Loaded BPF protocol xbox-dvd

*Sometimes (or should I say very often the commande does not work and I have fu... no idea why so in this case just halt and unplug power ...)

Now we should be able to receive data:  
`pi@raspberrypi:~/Dev/$ ir-keytable -t -s rc1`  
 

In the following sections I will try to record the KEY_POWER of my Sony remote.  

### Record keys with ir-ctl as raw codes:  
`pi@raspberrypi:~/Dev/$ ir-ctl -d /dev/lirc-rx -r`  

```
+2439 -560 +1240 -562 +638 -562 +1239 -561 +638 -562 +1238 -563 +637 -563 +636 -564 +1237 -587 +587 -591 +633 -566 +636 -564 +634 # timeout 18318
+2415 -561 +1235 -566 +609 -613 +1187 -613 +611 -568 +1209 -591 +633 -566 +610 -613 +1212 -566 +633 -589 +586 -591 +633 -590 +586 # timeout 17310
+2407 -612 +1188 -590 +632 -590 +1188 -591 +632 -589 +1188 -591 +609 -614 +610 -567 +1235 -589 +611 -567 +609 -592 +609 -614 +586 # timeout 20261
```

**HUGE WARNING**: When we have enabled all protocols the format of ir-ctl is different and instead of having the 3 lines as above we have a unique
line with all data in a row like this:  
```
+2434 -556 +1241 -561 +638 -562 +1238 -562 +637 -562 +1239 -562 +636 -564 +635 -565 +1235 -565 +635 -565 +634 -566 +635 -571 +603 -25818 +2410 -610 +1188 -591 +633 -567 +1210 -591 +614 -587 +1208 -592 +636 -585 +592 -608 +1188 -591 +609 -613 +592 -609 +585 -615 +609 -25793 +2410 -590 +1235 -587 +587 -613 +1212 -590 +585 -591 +1234 -566 +633 -589 +586 -592 +1233 -567 +635 -589 +599 -601 +585 -614 +586 # timeout 40150
```

It seems the following protocols change the format: jvc sharp xmp imon



### Send a key using a file containing raw data:  
`pi@raspberrypi:~/Dev/$ ir-ctl -v -d /dev/lirc-tx --send=SONY-KEY_POWER.txt' with data like +2400 -600 +1200 -600 +600 -600 +1200 -600 ... `  
  
### Send a key using a toml file:  
`pi@raspberrypi:~/Dev/$ ir-ctl -v -d /dev/lirc-tx -k sony-raw.toml -K KEY_POWER`  


