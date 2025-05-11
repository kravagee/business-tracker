from requests import post, get, put, delete

''' create_worker '''

print(post('http://127.0.0.1:8080/api/business/1/create_worker',
           json={'surname': 'Jobs', 'name': 'Steve', 'position': 'dryer', 'salary': 123}
           , params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}).json())