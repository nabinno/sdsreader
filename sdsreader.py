import arrow, logging, time

from pmuploader import PmDataUploader 
from sdserror import SdsError, SdsNoPacketError
from sdssensor import SdsSensor 

LOGLEVEL = logging.INFO
PORT = '/dev/serial0'
# Time delta between measurements, in seconds:
SAMPLING_PERIOD = 15 
URL = "http://dusty.pythonanywhere.com/pm/save/"
                  
def loop():
    while True:
        try:
            measurement = pmSensor.getMeasurement()
            measurement['time'] = arrow.now()
            uploader.sendMeasurement(measurement)
            time.sleep(pmSensor.samplingPeriod)
        except SdsError as e:
            logging.error("SDS error: %s %s", type(e), e.args)

if __name__ == "__main__":
    logging.basicConfig(format = '%(asctime)s [%(levelname)s] %(message)s',
                        level = LOGLEVEL)
    print("Starting reading SDS PM sensor on port", PORT)
    try:
        pmSensor = SdsSensor(PORT, SAMPLING_PERIOD)
        pmSensor.setId()
        print("Sensor ID:", pmSensor.id)
        print("Sampling period:", pmSensor.samplingPeriod, "s")
        uploader = PmDataUploader(URL)
        loop()
    except SdsNoPacketError as e:
        print(e.message)
    except Exception as e:
        logging.error("%s %s", type(e), e.args)
        raise
