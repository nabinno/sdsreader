import glob, logging, os, pickle, requests, tempfile, time

class PmDataUploader:

    def __init__(self, url):
        self.faildate = 0
        self.url = url
        self.writecount = 0

    def file_get_contents(self, filename):
        records = []
        with open(filename, 'rb') as file:
            while True:
                try:
                    record = pickle.load(file)
                    records.append(record)
                except EOFError:
                    break            
            return records
                
    def file_put_contents(self, filename, data):
        with open(filename, 'ab') as file:
            #file.write(str(data['time']) + "; %.1f; %.1f\n" % (data['pm25'], data['pm10']))
            pickle.dump(data, file)
            
    def httpGet(self, datarecord):
        # sending get request and saving the response as response object
        response = requests.get(url = self.url, params = datarecord)
        logging.info("Server response: %s", response.text)        
        
    def sendMeasurement(self, datarecord):
        if self.writecount == 20:
            logging.debug("Persistent storage file too big. Will create new one.")
            self.faildate = 0
            self.writecount = 0
        if self.faildate == 0:
            self.faildate = time.strftime("%Y-%m-%d-%H-%M-%S")
        filePath = os.path.join(os.path.dirname(__file__),
                                "pending." + self.faildate + ".pickle")
        logging.debug("Persistent storage file is: %s", filePath)

        try:
            self.httpGet(datarecord)
            self.uploadQueue()
        except requests.exceptions.ConnectionError as e:
            logging.error("Connection to remote server failed: %s %s", type(e), e.args)
            self.file_put_contents(filePath, datarecord)
            self.writecount += 1
            logging.info("Data saved in %s", filePath)

    def uploadQueue(self):
        path = os.path.dirname(os.path.abspath(__file__))
        for filePath in glob.glob(path+'/*.pickle'):
            logging.info("Uploading data file %s...", filePath)
            records = self.file_get_contents(filePath)
            try:
                for record in records:
                    self.httpGet(record)
                os.remove(filePath)
                logging.info("File %s uploaded", filePath)                
            except requests.exceptions.ConnectionError as e:
                logging.error("Connection to remote server failed: %s %s", type(e), e.args)
                logging.warning("File %s still pending", filePath)                


        
                
                    

            
    
