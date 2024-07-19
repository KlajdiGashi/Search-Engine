import aiohttp
import asyncio
from faker import Faker

fake = Faker()
url = "http://127.0.0.1:5000/api/users"

# Number of dummy users to create
num_users = 20000

async def create_user(session):
    data = {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password()
    }

    async with session.post(url, json=data) as response:
        status = response.status
        try:
            result = await response.json()
        except aiohttp.ContentTypeError:
            result = await response.text()
        return status, result

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [create_user(session) for _ in range(num_users)]
        responses = await asyncio.gather(*tasks)
        
        for status, result in responses:
            print(f"Status code: {status}")
            print(result)

# Run the main function
asyncio.run(main())
