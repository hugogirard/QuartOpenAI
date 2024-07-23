from quart import Quart, abort, request, jsonify
from openai import AsyncAzureOpenAI
from Models.ChatHistory import ChatHistory, Message, Usage
from datetime import datetime,timezone
from dotenv import load_dotenv
import uuid
import json
import os

load_dotenv()
open_ai_key = os.getenv('OPEN_AI_KEY')
open_ai_endpoint = os.getenv('OPEN_AI_ENDPOINT')
open_ai_chat_model = os.getenv('OPEN_AI_CHAT_MODEL')
open_ai_version = os.getenv('OPEN_AI_VERSION')

_history = dict()

system_prompt = ("You are an intelligent assistant helping people answer their questions" +
                "Use 'you' to refer to the individual asking the questions even if they ask with 'I'. ")


question_few_shot = ("Q: What is human life expectancy in the United States? ")
answer_few_shot = """{ "answer": "Human life expectancy in the United States is 78 years.", "                                    
                       "citations": [
                            {
                                "title": "life-expectancy",
                                "url": "https://www.cdc.gov/nchs/fastats/life-expectancy.htm"
                            },
                            {
                                "title": "NCHS",
                                "url": "https://www.cdc.gov/nchs/data/nvsr/nvsr68/nvsr68_07-508.pdf"
                            },
                            {
                                "title": "HUS",
                                "url": "https://www.cdc.gov/nchs/data/hus/2019/022-508.pdf"
                            }
                       ]"""

open_ai_client = AsyncAzureOpenAI(api_key=open_ai_key,
                                  api_version=open_ai_version,
                                  azure_endpoint=open_ai_endpoint
)

app = Quart(__name__)

@app.delete('/api/chat/<conversation_id>')
async def delete(conversation_id ):
    if conversation_id in _history:
        del _history[conversation_id]
        return '', 204
    else:
        return '', 404

@app.delete('/api/chat')
async def get():
    _history = dict()
    return '', 204

@app.post('/api/chat')
async def chat():

    try:
        data = await request.get_json()

        prompt = data.get('prompt')
        conversation_id = data.get('conversation_id')

        if not prompt:
            'No prompt provided', 400

        message_prompts = [{"role": "system", "content": system_prompt}]
        # message_prompts.append({"role": "user", "content": question_few_shot})
        # message_prompts.append({"role": "assistant", "content": answer_few_shot})
        #message_prompts.append({"role": "user", "content": prompt})

        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            _history[conversation_id] = ChatHistory(conversation_id=conversation_id, messages=[], usage=Usage(0,0,0))
            message = Message(id=str(uuid.uuid4()), role="user", content=prompt, date=datetime.now(timezone.utc),citation=None)
            _history[conversation_id].messages.append(message)            
        elif not _history[conversation_id]:
            return 'Conversation not found', 404
        else:
            message = Message(id=str(uuid.uuid4()), role="user", content=prompt, date=datetime.now(timezone.utc),citation=None)
            _history[conversation_id].messages.append(message)            

        
        for message in _history[conversation_id].messages:                
            message_prompts.append({ "role": message.role, "content": message.content})

        response = await open_ai_client.chat.completions.create(model=open_ai_chat_model,
                                                                messages=message_prompts,
                                                                max_tokens=2048,
                                                                temperature=0.9
        )    
        
                 
        #return response.choices[0].message.content
        citations = [
                {
                    "title": "life-expectancy",
                    "url": "www.microsoft.com"
                },
                {
                    "title": "NCHS",
                    "url": "www.microsoft.com"
                },
                {
                    "title": "HUS",
                    "url": "www.microsoft.com"
                }
            ]        
        message = Message(id=str(uuid.uuid4()), role="assistant", content=response.choices[0].message.content, date=datetime.now(timezone.utc),citation=citations)
        _history[conversation_id].messages.append(message)        
        _history[conversation_id].usage = Usage(response.usage.completion_tokens, response.usage.prompt_tokens, response.usage.total_tokens)
        return _history[conversation_id].to_json()
    except Exception as e:
        app.logger.error(e)
        abort(500)

app.run()