from requests import get, post, delete, put

''' get_stat_business '''

print(get('http://127.0.0.1:8080/api/business/get_stat_business/1',
          params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}).json())

print(get('http://127.0.0.1:8080/api/business/get_stat_business/1').json())

print(get('http://127.0.0.1:8080/api/business/get_stat_business/1', params={'api_key': '123'}).json())

''' add_manager '''

print(
    post('http://127.0.0.1:8080/api/business/1/add_manager/2', params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}))

''' delete_manager '''

print(delete('http://127.0.0.1:8080/api/business/1/delete_manager/2',
             params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}).json())

''' edit_worker '''

print(put('http://127.0.0.1:8080/api/business/1/edit_worker/1', params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'},
          json={'surname': 'ФГОЫВ', 'name': 'Лёха', 'position': 'ewt', 'salary': 100}).json())

''' delete worker '''

print(delete('http://127.0.0.1:8080/api/business/1/delete_worker/1',
             params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}).json())

''' edit_product '''

print(put('http://127.0.0.1:8080/api/business/1/edit_product/1',
          json={'status': 'Использован',
                'name': 'батон',
                'price': 200},
          params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}).json())

''' get_products '''

print(get('http://127.0.0.1:8080/api/business/get_products/1',
          params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}).json())

''' get_workers '''

print(get('http://127.0.0.1:8080/api/business/get_workers/1',
          params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}).json())

''' get_worker '''

print(get('http://127.0.0.1:8080/api/business/1/get_worker/1',
          params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}).json())

''' create_worker '''

print(post('http://127.0.0.1:8080/api/business/1/create_worker',
           json={'surname': 'Jobs', 'name': 'Steve', 'position': 'dryer', 'salary': 123}
           , params={'api_key': 'CHyHmU9frM4u32p7RnfRmL0y1ytMXdcr'}).json())
