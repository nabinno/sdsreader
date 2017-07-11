import glob, logging, os, pickle, requests, tempfile, time

class PmDataUploader:

    def __init__(self, url):
        self.faildate = 0
        self.url = url
        self.writecount = 0
        self.session = requests.Session()
        self.csrftoken = self.getCsrfToken()

    def file_get_contents(self, filename):
        tuples = []
        with open(filename, 'rb') as file:
            while True:
                try:
                    measurement = pickle.load(file)
                    tuples.extend(list(measurement.items()))
                except EOFError:
                    break            
            return tuples
                
    def file_put_contents(self, filename, measurement):
        with open(filename, 'ab') as file:
            pickle.dump(measurement, file)

    def getCsrfToken(self):
        response = self.session.get(self.url)
        logging.debug("url = %s", response.url)
        logging.debug("Server response: %s", response.text) 
        logging.debug("cookie jar = %s", response.cookies)
        cookies = dict(response.cookies)
        logging.debug("cookies = %s", cookies)
        return cookies['csrftoken']      
            
    def httpPost(self, tuples):
        logging.debug("data tuples: %s", tuples)
        # Adding csrf token to list of tuples, otherwise it's not
        # possible to post data record 
        tuples.append(('csrfmiddlewaretoken', self.csrftoken))
        logging.debug("data tuples: %s", tuples)

        response = self.session.post(url = self.url, data = tuples)
        logging.debug("cookie jar = %s", response.cookies)
        
        logging.info("Server response: %s", response.text)        
        
    def sendMeasurement(self, measurement):
        if self.writecount == 20:
            logging.debug("Persistent storage file too big. Will create new one.")
            self.faildate = 0
            self.writecount = 0
        if self.faildate == 0:
            self.faildate = time.strftime("%Y-%m-%d-%H-%M-%S")
        filePath = os.path.join(os.path.dirname(__file__),
                                "pending." + self.faildate + ".pickle")
        logging.debug("Persistent storage file is: %s", filePath)

        # Transform the measurement dictionary in a list of tuples
        tuples = list(measurement.items())
         
        try:
            self.httpPost(tuples)
            self.uploadQueue()
        except requests.exceptions.ConnectionError as e:
            logging.error("Connection to remote server failed: %s %s", type(e), e.args)
            self.file_put_contents(filePath, measurement)
            self.writecount += 1
            logging.info("Data saved in %s", filePath)            

    def uploadQueue(self):
        path = os.path.dirname(os.path.abspath(__file__))
        for filePath in glob.glob(path+'/*.pickle'):
            logging.info("Uploading data file %s...", filePath)
            tuples = self.file_get_contents(filePath)
            try:
                self.httpPost(tuples)
                os.remove(filePath)
                logging.info("File %s uploaded", filePath)                
            except requests.exceptions.ConnectionError as e:
                logging.error("Connection to remote server failed: %s %s", type(e), e.args)
                logging.warning("File %s still pending", filePath)                


        
                
                    

            
    
