from requests import get, post, delete, put

''' get_stat_user '''
print(get('http://127.0.0.1:8080/api/users/get_stat_user/1', params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}).json())

print(get('http://127.0.0.1:8080/api/users/get_stat_user/1').json())

print(get('http://127.0.0.1:8080/api/users/get_stat_user/1', params={'api_key': '1241'}).json())


''' add_business '''

print(post('http://127.0.0.1:8080/api/users/1/add_business', json={'name': 'test',
                                                            'description': 'test'}, params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}))


''' get_business '''

print(get('http://127.0.0.1:8080/api/users/get_businesses/1', params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}).json())