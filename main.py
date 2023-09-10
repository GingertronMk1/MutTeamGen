from requests import get


def make_mut_gg_request(url = ''):
  return get(f'https://www.mut.gg/{url}')



body = make_mut_gg_request('players')
print(body.content)
