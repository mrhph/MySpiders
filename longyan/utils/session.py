import requests

def get(*args, **kwargs):
    s = requests.session()
    s.keep_alive = False
    flag = 0
    while flag < 20:
        try:
            flag += 1
            response = s.get(*args, **kwargs)
            if response.status_code != 200:
                raise Exception
        except:
            continue
        return response
    return None