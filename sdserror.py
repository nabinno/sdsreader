class SdsError(Exception):
    """Base class for exceptions in this module."""
    pass

class SdsChecksumError(SdsError):
    """Exception raised for errors in data payload.

    Attributes:
        message -- explanation of the error
        checksum_calc -- checksum calculated from payload
        checksum_pkt -- checksum in packet (packet[8])
    """

    def __init__(self, message):
        self.message = message

class SdsIdError(SdsError):
    """Exception raised for unconsistent sensor ID in packet

    Attributes:
        message -- explanation of the error
        idFromPacket -- sensor ID contained in package
    """

    def __init__(self, message, idFromPacket):
        self.message = message
        self.idFromPacket = idFromPacket

class SdsNoPacketError(SdsError):
    """Exception raised for errors in data packet header or trailer.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message        
    
class SdsPacketError(SdsError):
    """Exception raised for errors in data packet header or trailer.

    Attributes:
        message -- explanation of the error
        header1 -- header byte 1 (packet[0])
        header2 -- header byte 2 (packet[1])
        trailer -- trailer (packet[9])
    """

    def __init__(self, message, header1, header2, trailer):
        self.message = message
        self.header1 = header1
        self.header2 = header2
        self.trailer = trailer
        
class SdsValueError(SdsError):
    """Exception raised for unconsistent sensor ID in packet

    Attributes:
        message -- explanation of the error
        pm25 -- pm25 value read from package
        pm10 -- pm10 value read from package
    """

    def __init__(self, message, pm25, pm10):
        self.message = message
        self.pm25 = pm25
        self.pm10 = pm10
