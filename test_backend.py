import aiohttp
import asyncio
import json


async def get_jwt_token():
    url = 'http://localhost:3000/api/auth'
    headers = {'Authorization': 'Bearer Just-a-test-token'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['token']
            else:
                print(
                    f'Failed to get JWT token: {response.status}, reason: {response.reason}'
                )


async def test_websocket():
    encoded_jwt = await get_jwt_token()

    session = aiohttp.ClientSession()
    ws_url = f'ws://localhost:3000/ws?token={encoded_jwt}'
    try:
        async with session.ws_connect(ws_url) as ws:
            print('WebSocket connected')

            await ws.send_str('{"action": "initialize", "args": {"agent_cls": "PlannerAgent"}}')  # noqa: Q000
            print('First message sent. Waiting before sending the next one.')

            # 延时一段时间后发送第二个请求
            await asyncio.sleep(5)  # 延时5秒
            await ws.send_str('{"action": "start", "args": {"task": "write a hello world in python"}}')  # noqa: Q000
            print('Second message sent. Waiting for a response.')

            # 处理服务器响应
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print(f'Message from server: {msg.data}')
                    response_data = json.loads(msg.data)
                    if response_data.get('action') == 'finish':
                        print("Received 'finish' action. Closing connection.")
                        await ws.close()
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break

        async with session.get('http://localhost:3000/api/plan', headers={'Authorization': f'Bearer {encoded_jwt}'}) as response:
            if response.status == 200:
                data = await response.json()
                print('Plan:', data)
            else:
                print(
                    f'Failed to fetch plan: {response.status}, reason: {response.reason}'
                )
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        await session.close()

asyncio.run(test_websocket())
