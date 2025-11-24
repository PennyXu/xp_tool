import os
import asyncio
import httpx
from openai import AsyncOpenAI
from tqdm import tqdm

class AsyncCallAiTqdm:
    def __init__(self, max_connections=10,api_key=None, baseurl=None):
        self.client = AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY') if not api_key else api_key,
            base_url=baseurl,
            http_client=httpx.AsyncClient(limits=httpx.Limits(max_connections=max_connections))
        )
        self._prompt = ''

    @property
    def prompt(self):
        return self._prompt

    @prompt.setter
    def prompt(self, content):
        self._prompt = content

    async def get_openai_response(self, text):
        try:
            response = await self.client.chat.completions.create(
                model='qwen-max',
                messages=[
                    {'role': 'system', 'content': self._prompt},
                    {'role': 'user', 'content': text}
                ]
            )
            return response.choices[0].message.content.strip() if response.choices else "无返回结果"
        except Exception as e:
            return f"请求失败: {str(e)}"

    async def chat(self, text):
        async def task_with_idx(idx, content):
            result = await self.get_openai_response(content)
            return (idx, result)

        tasks = [task_with_idx(idx, content) for idx, content in enumerate(text)]
        
        results_with_idx = []
        with tqdm(total=len(tasks), desc="AI请求处理中", ncols=80, colour='green') as pbar:
            for task in asyncio.as_completed(tasks):
                idx_and_result = await task
                results_with_idx.append(idx_and_result)
                pbar.update(1)
        
        results_with_idx.sort(key=lambda x: x[0])
        results = [res for _, res in results_with_idx]
        return results
