from quart import Quart, abort, request, jsonify
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
open_ai_key = os.getenv('OPEN_AI_KEY')
open_ai_endpoint = os.getenv('OPEN_AI_ENDPOINT')
open_ai_chat_model = os.getenv('OPEN_AI_CHAT_MODEL')
open_ai_version = os.getenv('OPEN_AI_VERSION')

system_prompt = ("You are an intelligent assistant helping people answer their questions" +
                "Use 'you' to refer to the individual asking the questions even if they ask with 'I'. "+
                "Provide citations that base your answers on facts and references. Try to provides 3 if possible")


question_few_shot = ("Q: What is human life expectancy in the United States? ")
answer_few_shot = """A: Human life expectancy in the United States is 78 years. "                                    
                     Citations: 
                       1. https://www.cdc.gov/nchs/fastats/life-expectancy.htm
                       2. https://www.cdc.gov/nchs/data/nvsr/nvsr68/nvsr68_07-508.pdf
                       3. https://www.cdc.gov/nchs/data/hus/2019/022-508.pdf"""

open_ai_client = AsyncAzureOpenAI(api_key=open_ai_key,
                                  api_version=open_ai_version,
                                  azure_endpoint=open_ai_endpoint
)

app = Quart(__name__)

@app.post('/api/chat')
async def chat():

    try:
        data = await request.get_json()

        prompt = data.get('prompt')

        if not prompt:
            'No prompt provided', 400

        message_prompts = [{"role": "system", "content": system_prompt}]
        message_prompts.append({"role": "user", "content": question_few_shot})
        message_prompts.append({"role": "assistant", "content": answer_few_shot})
        message_prompts.append({"role": "user", "content": prompt})

        response = await open_ai_client.chat.completions.create(model=open_ai_chat_model,
                                                                messages=message_prompts,
                                                                max_tokens=1024,
                                                                temperature=0.7
        )    

        return response.choices[0].message.content,200    
    except Exception as e:
        app.logger.error(e)
        abort(500)

app.run()