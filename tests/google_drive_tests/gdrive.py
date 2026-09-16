import unittest
from config import Config #import this to add the module to sys path
from datetime import datetime as dt
from os import remove,path

from google_drive import worker, get_service

class TestGoogleDrive(unittest.TestCase):
    def setUp(self):
        self.secrets_file_path = Config.GOOGLE_DRIVE_SECRETS_JSON_PATH
        self.api_name = 'drive'
        self.api_version = 'v3'
        self.scope_readonly = 'https://www.googleapis.com/auth/drive.metadata.readonly'
        self.scope_write = 'https://www.googleapis.com/auth/drive'
        self.current_time = dt.now().strftime('%Y%m%d%H%M%S')

    def testCreateService(self):
        try:
            service = get_service(api_name=self.api_name,api_version=self.api_version,
                                  scopes=self.scope_write,
                                  key_file_location=self.secrets_file_path
                                  )
            self.assertIsNotNone(service,msg='Could not create service')
        except:
            self.fail("Could not create service")

    def testReadDriveFiles(self):
        worker_run = worker(key_file_location=self.secrets_file_path)
        result = worker_run.read_drive_files()
        code = result.get('code')
        self.assertEqual(code,200,msg='Could not read drive files')

    def testUploadFile(self):
        worker_run = worker(key_file_location=self.secrets_file_path)
        filename = self.current_time+'test.txt'
        with open(filename,'w') as f:
            f.write('Hello World')

        result = worker_run.upload_file_to_drive(filename=filename,file_path=filename)
        code = result.get('code')
        remove(filename)
        self.assertEqual(code,200,msg='Could not upload file to drive')
        
    def testDownloadFile(self):
        worker_run = worker(key_file_location=self.secrets_file_path)
        filename = self.current_time+'test.txt'
        result = worker_run.download_drive_file(filename=filename,download_path='.')
        # print(result)
        code = result.get('code')
        if path.exists(filename):
            remove(filename)

        self.assertEqual(code,200,result)#msg='Could not download file from drive')



if __name__ == '__main__':
    unittest.main()