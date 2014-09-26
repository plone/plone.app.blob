from ZPublisher.HTTPRequest import HTTPRequest
from StringIO import StringIO
from base64 import decodestring
from os.path import dirname, join
from plone.app.blob import tests

test_environment = {
    'CONTENT_TYPE': 'multipart/form-data; boundary=12345',
    'REQUEST_METHOD': 'POST',
    'SERVER_NAME': 'localhost',
    'SERVER_PORT': '80',
}

upload_request = '''
--12345
Content-Disposition: form-data; name="file"; filename="%s"
Content-Type: application/octet-stream
Content-Length: %d

%s

'''


def makeFileUpload(data, filename):
    request_data = upload_request % (filename, len(data), data)
    req = HTTPRequest(StringIO(request_data), test_environment.copy(), None)
    req.processInputs()
    return req.form.get('file')


def getImage():
    gif = 'R0lGODlhAQABAPAAAPj8+AAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
    return decodestring(gif)


def getFile(filename):
    """ return a file object from the test data folder """
    filename = join(dirname(tests.__file__), 'data', filename)
    return open(filename, 'r')


def getData(filename):
    """ return file data """
    return getFile(filename).read()


def hasLinguaPlone():
    """ test if LinguaPlone is available """
    try:
        from Products import LinguaPlone
        LinguaPlone     # make pyflakes happy...
        return True
    except ImportError:
        msg = 'WARNING: LinguaPlone not found. Skipping tests.'
        print '*' * len(msg)
        print msg
        print '*' * len(msg)
        return False
