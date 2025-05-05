import pycurl
import json
from io import BytesIO

c = None
endpoint = None

def curl_setup(endpoint:str) -> None:
    global c
    c = pycurl.Curl()
    c.setopt(c.URL, endpoint)

def curl_close() -> None:
    if c is not None:
        c.close()

def curl_get_embedding(model_name:str, input:str | list[str], ignore_ssl_verification:bool = False) -> list[float]:

    if isinstance(input, str):
        input_as_list = [input]
    elif isinstance(input, list):
        input_as_list = input
    else:
        raise TypeError("Input must be a string or list of strings that represent raw input to be encoded.")
        
    data = {
     "model": model_name,
     "input": input_as_list,
     "encoding_format":"float"
    }

    post_data = json.dumps(data)
    headers = ['Content-Type: application/json']
    buffer = BytesIO()

    c.setopt(c.POSTFIELDS, post_data)
    c.setopt(c.HTTPHEADER, headers)
    c.setopt(c.WRITEDATA, buffer)

    if ignore_ssl_verification:
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
    
    c.perform()
    
    response = buffer.getvalue()
    
    result = response.decode('utf-8')
    
    #print(result[0:1000])b

    embeddings = json.loads(result)

    result = list()

    for e in embeddings['data']:
        result.append(e['embedding'])
    
    return embeddings