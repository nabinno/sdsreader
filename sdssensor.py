import logging, serial
from sdserror import *

class SdsSensor:
    def __init__(self, port = "/dev/serial0", samplingPeriod = 15):
        self.serial = serial.Serial(port = port, baudrate = 9600)
        self.serial.setTimeout(1.5)
        self.samplingPeriod = samplingPeriod
        self.id = "unknown"            
 
    def getIdFromPacket(self, packet):
        id = "sds-"
        for i in range(6,8):
            hvol = packet[i]
            hhex = '%02x'%hvol
            id += hhex
        return id

    def getMeasurement(self):
        packet = self.readPacket()
            
        if (not self.isIdOk(packet)):
            raise SdsIdError("Data packet contains wrong sensor ID",
                             self.getIdFromPacket(packet))

        pm25=(int(packet[2])+int(packet[3])*256)/10.0
        pm10=(int(packet[4])+int(packet[5])*256)/10.0
        if(pm25 > 999.9 or pm10 > 999.9):
            raise SdsValueError("PM values out of range", pm25, pm10)
                   
        return {'id': self.id,
                'pm25': pm25, 
                'pm10': pm10}            
        
    def hexFormat(self, packet):  
        hexString = ''  
        hLen = len(packet)  
        for i in range(hLen):  
            hvol = packet[i]
            hhex = '%02x'%hvol  
            hexString += hhex + ' '  
        return hexString
    
    def isChecksumOk(self, packet):
        checksum=0
        for i in range(6):
            checksum=checksum+int(packet[2+i])
        if checksum % 256 == packet[8]:
            return True
        return False
    
    def isIdOk(self, packet):    
        if (self.getIdFromPacket(packet) == self.id):
            return True
        return False            
                
    def readPacket(self):
        self.serial.flushInput()
        packet = self.serial.read(10) # read 10 bytes
        logging.debug("Packet content: %s", self.hexFormat(packet))
# packet format (from www.inovafitness.com):
# AA C0 PM25_Low PM25_High PM10_Low PM10_High ID_1 ID_2 CRC AB
# 0  1  2        3         4        5         6    7    8   9
        if (packet[0] != 0xaa or packet[1] != 0xc0 or packet[9] != 0xab):
            raise SdsPacketError("Packet has wrong header or trailer",
                                 packet[0], packet[1], packet[9])
        if (not self.isChecksumOk(packet)):
            raise SdsChecksumError("Checksum error")
        return packet

    def setId(self):
        packet = self.readPacket()
        self.id = self.getIdFromPacket(packet)    
