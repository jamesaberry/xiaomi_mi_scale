# Xiaomi Mi Scale

Code to read weight measurements from [Mi Body Composition Scale](https://www.mi.com/global/mi-body-composition-scale/) (aka Xiaomi Mi Scale V2)

![Mi Scale](https://github.com/lolouk44/xiaomi_mi_scale/blob/master/Screenshots/Mi_Scale.png)

Note: Framework is present to also read from Xiaomi Scale V1.  I am using the V1 scale and can confirm its working for me.

## Setup:
1. Retrieve the scale's MAC Address (you can identify your scale by looking for `MIBCS` entries) using this command:
```
$ sudo hcitool lescan
LE Scan ...
F8:04:33:AF:AB:A2 [TV] UE48JU6580
C4:D3:8C:12:4C:57 MIBCS
[...]
```
1. Copy all files
1. Open `Xiaomi_Scale.py`
1. Assign Scale's MAC address to variable `MISCALE_MAC`
1. Edit user logic/data (Currently only set up for one user.)

## How to use?
- Must be executed with Python 3 else body measurements are incorrect.
- Must be executed as root, therefore best to schedule via crontab every 5 min (so as not to drain the battery):
```
*/5 * * * * python3 /path-to-script/Xiaomi_Scale.py
```

## Fork Changes
- Removed Home-Assistant support as I will not be using Home Assistant to track data.
- Added monodb support as I will be using monodb to track data.

## To Do
- I plan to put together a very basic webpage to display the data this script collects. I plan to run the page on the same machine that i will run this script on and so I may include it in this project just to keep everything together.

## Acknowledgements:
Thanks to @lolouk44 (https://github.com/lolouk44/xiaomi_mi_scale) from which this project is forked.
Thanks to @syssi (https://gist.github.com/syssi/4108a54877406dc231d95514e538bde9) and @prototux (https://github.com/wiecosystem/Bluetooth) for their initial code
