from requests import get, post, delete, put


print(get('http://127.0.0.1:8080/api/users/get_stat_user/1', params={'api_key': '8vXJjjHEaPkxtAZTaNvOTZJzLJecX1Kl'}))