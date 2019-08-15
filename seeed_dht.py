#!/usr/bin/env python
#
# This code is for
#   Grove - Temperature & Humidity Sensor (DHT11)
#     (https://www.seeedstudio.com/Grove-Temperature-Humidity-Sensor-DHT1-p-745.html)
#   Grove - Temperature & Humidity Sensor Pro (AM2302)
#     (https://www.seeedstudio.com/Grove-Temperature-Humidity-Sensor-Pro-AM230-p-838.html)
#
# which is consists of a capacitive sensor element used for measuring relative humidity
# and a negative temperature coefficient(NTC) thermistor used for measuring temperature.
#
# This is the library for Grove Base Hat which used to connect grove sensors for raspberry pi.
#
from grove.gpio import GPIO
from grove.i2c import Bus
import time

class DHT(object):
    DHT_TYPE = {
        'DHT11': '11',
        'DHT22': '22',
        'DHT10': '10'
    }

    DEFAULT_ADDR    = 0x38
    RESET_REG_ADDR  = 0xba
    MAX_CNT = 320
    PULSES_CNT = 41


    def __init__(self, dht_type, pin = 12,bus_num = 1):        
        if dht_type != self.DHT_TYPE['DHT11'] and dht_type != self.DHT_TYPE['DHT22'] and dht_type != self.DHT_TYPE['DHT10']:
            print('ERROR: Please use 11|22|10 as dht type.')
            exit(1)
        self.dht_type = dht_type
        if dht_type == self.DHT_TYPE['DHT10']:
            self.bus = Bus(bus_num)
            self.addr = self.DEFAULT_ADDR
            self._dht10_init()
        else:
            self.pin = GPIO(pin, GPIO.OUT)
            self._last_temp = 0.0
            self._last_humi = 0.0

    @property
    def dht_type(self):
        return self._dht_type

    @dht_type.setter
    def dht_type(self, type):
        self._dht_type = type

    ######################## dht10 ############################

    def _dht10_start_mess(self):
        reg_set = [0x33,0x00]
        self.bus.write_i2c_block_data(self.addr,0xac,reg_set)

    def _dht10_reset(self):
        self.bus.write_byte(self.addr,self.RESET_REG_ADDR)
    
    def _dht10_set_system_cfg(self):
        reg_set = [0x08,0x00]
        self.bus.write_i2c_block_data(self.addr,0xe1,reg_set)

    def _dht10_read_status(self):
        return self.bus.read_byte_data(self.addr,0)

    def _dht10_init(self):

        time.sleep(.5)
        self._dht10_reset()
        # delay is needed after reset
        time.sleep(.3)

        self._dht10_set_system_cfg()
        status = self._dht10_read_status()
        # we must check the calibrate flag, bit[3] : 1 for calibrated ok,0 for Not calibrated.
        while (status & 0x08 != 0x08):
            print("try calibrated again!n\n")
            self._dht10_reset()
            time.sleep(.5)
            self.bus.dth10_set_system_cfg()
            status = self._dht10_read_status()
            time.sleep(.5)

    #########################################################
    def _read(self):
        if self.dht_type == self.DHT_TYPE['DHT10']:
            t = 0
            h = 0
            self._dht10_start_mess()
            time.sleep(.075)
            # we must check the device busy flag, bit[7] : 1 for busy ,0 for idle.
            while((self._dht10_read_status() & 0x80) != 0):
                time.sleep(.5)
                print("wait for device not busy")
            from smbus2 import SMBus,i2c_msg,SMBusWrapper
            with SMBusWrapper(1) as bus:
                msg = i2c_msg.read(self.addr,6)
                data = bus.i2c_rdwr(msg)
            data = list(msg)
            t = (t | data[1]) << 8
            t = (t | data[2]) << 8
            t = (t | data[3]) >> 4

            h = (h | data[3]) << 8
            h = (h | data[4]) << 8
            h = (h | data[5]) & 0xfffff

            t = t * 100.0 / 1024 / 1024
            h = h * 200.0 / 1024 / 1024 - 50
            #print(data)
            return t,h
        # Send Falling signal to trigger sensor output data
        # Wait for 20ms to collect 42 bytes data
        else:
            self.pin.dir(GPIO.OUT)

            self.pin.write(1)
            time.sleep(.2)

            self.pin.write(0)
            time.sleep(.018)

            self.pin.dir(GPIO.IN)
            # a short delay needed
            for i in range(10):
                pass

            # pullup by host 20-40 us
            count = 0
            while self.pin.read():
                count += 1
                if count > self.MAX_CNT:
                    # print("pullup by host 20-40us failed")
                    return None, "pullup by host 20-40us failed"

            pulse_cnt = [0] * (2 * self.PULSES_CNT)
            fix_crc = False
            for i in range(0, self.PULSES_CNT * 2, 2):
                while not self.pin.read():
                    pulse_cnt[i] += 1
                    if pulse_cnt[i] > self.MAX_CNT:
                        # print("pulldown by DHT timeout %d" % i)
                        return None, "pulldown by DHT timeout %d" % i

                while self.pin.read():
                    pulse_cnt[i + 1] += 1
                    if pulse_cnt[i + 1] > self.MAX_CNT:
                        # print("pullup by DHT timeout %d" % (i + 1))
                        if i == (self.PULSES_CNT - 1) * 2:
                            # fix_crc = True
                            # break
                            pass
                        return None, "pullup by DHT timeout %d" % i


            total_cnt = 0
            for i in range(2, 2 * self.PULSES_CNT, 2):
                total_cnt += pulse_cnt[i]

            # Low level ( 50 us) average counter
            average_cnt = total_cnt / (self.PULSES_CNT - 1)
            # print("low level average loop = %d" % average_cnt)
        
            data = ''
            for i in range(3, 2 * self.PULSES_CNT, 2):
                if pulse_cnt[i] > average_cnt:
                    data += '1'
                else:
                    data += '0'
            
            data0 = int(data[ 0: 8], 2)
            data1 = int(data[ 8:16], 2)
            data2 = int(data[16:24], 2)
            data3 = int(data[24:32], 2)
            data4 = int(data[32:40], 2)

            if fix_crc and data4 != ((data0 + data1 + data2 + data3) & 0xFF):
                data4 = data4 ^ 0x01
                data = data[0: self.PULSES_CNT - 2] + ('1' if data4 & 0x01 else '0')

            if data4 == ((data0 + data1 + data2 + data3) & 0xFF):
                if self._dht_type == self.DHT_TYPE['DHT11']:
                    humi = int(data0)
                    temp = int(data2)
                elif self._dht_type == self.DHT_TYPE['DHT22']:
                    humi = float(int(data[ 0:16], 2)*0.1)
                    temp = float(int(data[17:32], 2)*0.2*(0.5-int(data[16], 2)))
            else:
                # print("checksum error!")
                return None, "checksum error!"

            return humi, temp

    def read(self, retries = 15):
        for i in range(retries):
            humi, temp = self._read()
            if not humi is None:
                break
        if humi is None:
            return self._last_humi, self._last_temp
        self._last_humi,self._last_temp = humi, temp
        return humi, temp

