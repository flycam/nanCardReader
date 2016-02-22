__author__ = 'stephan'

# requires pyserial, json, re
import serial
import json
import re
import time


class CardReader:
    def __init__(self, bus_addr):
        self.bus_addr = bus_addr

    def check(self, ser):
        # try communication
        try:
            ser.write("$%i/check\n" % self.bus_addr)
            res = ser.readline()
            res = re.sub(r'[^\x00-\x7F]+', ' ', res)
        except:
            self.log("Communication with node %i failed." % self.bus_addr)
            return 0

        if len(res) < 1:
            return 0  # no data

        try:
            decoded = json.loads(res.strip())
        except ValueError as err:
            return 0

        try:
            check_result_data = decoded['check_result']
            hasData = check_result_data['hasData']

            # has data
            if hasData == 1 and check_result_data['node'] == self.bus_addr:
                card_nr = check_result_data['cardnr']
                card_uid = check_result_data['uid']

                if card_nr == "000000000000":
                    check_result_data['cardnr'] = "UI%i" % int(card_uid, 16)
                    # print check_result_data['cardnr']
                return check_result_data
        except:
            self.log("ReadError")
        return 0

    def confirm(self, ser):
        ser.write("$%i/confirm\n" % self.bus_addr)
        res = ser.readline()

    def deny(self, ser):
        ser.write("$%i/deny\n" % self.bus_addr)
        res = ser.readline()

    def log(self, message):
        print(message)

# example

def testCardReader():
    ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=0.05)
    cr = CardReader(1)

    while 1:
        data = cr.check(ser)
        if data is not 0:
            cardNr = data['cardnr']
            print(cardNr)
            if cardNr == "158021227943":
                cr.confirm(ser)
            else:
                cr.deny(ser)
        time.sleep(0.2)
