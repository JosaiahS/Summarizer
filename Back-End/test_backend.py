
def test_upload_and_process():
    tester = app.test_client()
    with open('testingtesting.docx', 'rb') as f:
        response = tester.post('/upload', 
                               content_type='multipart/form-data',
                               data={'file': (f, 'sample.docx')})  

    print(response.data)  

if __name__ == "__main__":
    test_upload_and_process()
