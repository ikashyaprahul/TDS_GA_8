import os
import httpx
from openai import OpenAI

token = 'eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjEwMDMxNDlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.dNTWplTlAxzlj5_dhbcQlcHUsMkvlnj7DFDPV1LRNHU'

def test(url):
    print(f"Testing {url}...")
    try:
        client = OpenAI(base_url=url, api_key=token)
        res = client.chat.completions.create(model='gpt-4o-mini', messages=[{'role': 'user', 'content': 'hi'}])
        print("Success:", res.choices[0].message.content)
    except Exception as e:
        print("Error class:", type(e))
        print("Error details:", str(e))
        if hasattr(e, 'response') and e.response:
            print("Response:", e.response.text)

test('https://aipipe.org/openai/v1')
test('https://api.aiproxy.io/v1')
