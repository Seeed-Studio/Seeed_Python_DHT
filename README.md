# Seeed DHT

This is a powerful sister version of our Grove - Temperature&Humidity Sensor Pro. It has more complete and accurate performance than the basic version. The detecting range of this sensor is 5% RH - 99% RH, and -40°C - 80°C. And its accuracy reaches up to 2% RH and 0.5°C. A professional choice for applications that have relatively strict requirements.

This code is for
- [Grove - Temperature&Humidity Sensor Pro](https://www.seeedstudio.com/Grove-Temperature%26Humidity-Sensor-Pro%EF%BC%88AM2302%EF%BC%89-p-838.html)
- [Grove - Temperature & Humidity Sensor (DHT11)](https://www.seeedstudio.com/Grove-Temperature-Humidity-Sensor-DHT1-p-745.html)
- Grove - Temp & Humi Sensor v1.0 (DHT10)

# Dependencies
This driver depends on:
- [***grove.py***](https://github.com/Seeed-Studio/grove.py)

This is easy to install with the following command.
 ```
curl -sL https://github.com/Seeed-Studio/grove.py/raw/master/install.sh | sudo bash -s -
 ```
## Installing from PyPI

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally from PyPI. To install for current user:
```
pip3 install seeed-python-dht
```
To install system-wide (this may be required in some cases):
```
sudo pip3 install seeed-python-dht
```
To install in a virtual environment in your current project:
```
mkdir project-name && cd project-name
python3 -m venv .env
source .env/bin/activate
pip3 install seeed-python-dht
```

## Usage Notes

#### for DHT11,DHT22
First, Check the corresponding gpio number of the board:
```
pi@raspberrypi:~/Seeed_Python_DHT $ grove_gpio
Hat Name = 'Grove Base Hat RPi'
<pin> could be one of below values in the pin column for GPIO function
   And connect the device to corresponding slot
==============
 pin | slot
==============
  5  | D5   
 12  | PWM  
 16  | D16  
 18  | D18  
 22  | D22  
 24  | D24  
 26  | D26 
```
Next, initialize the sersor object:
```python
import seeed_dht
# for DHT11 the type is '11', for DHT22 the type is '22'
sensor = seeed_dht.DHT("11", 12)
```

#### for DHT10
DHT10 uses i2c protocol, So there is no need to specify an extra pin.  
Just add contents below:
```python
import seeed_dht
# for DHT11 the type is '11', for DHT22 the type is '22'
sensor = seeed_dht.DHT("10")
```

## Reading from the Sensor
To read from the sensor:
```
humi, temp = sensor.read()
print('DHT{0}, humidity {1:.1f}%, temperature {2:.1f}*'.format(sensor.dht_type, humi, temp))
```

## Contributing
If you have any good suggestions or comments, you can send issues or PR us.