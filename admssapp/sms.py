import urllib.request
import urllib.parse

apikey = 'nLWy7NSK6b0-3WN1JCPxe33GBDsjrKHNBHbVvxCL30'
numbers = '919005325725'
sender = 'TXTLCL'
message = 'ADMSS , On Establisment Day, Congratulations & Wellwishes' 

def sendSMS(apikey, numbers, sender, message):
    data =  urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,
        'message' : message, 'sender': sender})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return(fr)
 
resp =  sendSMS(apikey,numbers,sender,message)
print (resp)