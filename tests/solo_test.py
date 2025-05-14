from requests import post, get, put, delete

print(get('http://127.0.0.1:8080/api/business/get_stat_business/2', params={'api_key': 'mnBZCuuPk8zI8qsHzXPyod08aA3yocGx'}).json())