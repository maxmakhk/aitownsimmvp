import ollama
import os

print("OLLAMA_MODELS:", os.environ.get('OLLAMA_MODELS', 'Not set'))
print("OLLAMA_KEEP_ALIVE:", os.environ.get('OLLAMA_KEEP_ALIVE', 'Not set'))
print("OLLAMA_NUM_PARALLEL:", os.environ.get('OLLAMA_NUM_PARALLEL', 'Not set'))
print("OLLAMA_MAX_LOADED_MODELS:", os.environ.get('OLLAMA_MAX_LOADED_MODELS', 'Not set'))

# Basic chat with NPC personality
response = ollama.chat(
    model='gemma3:4b',
    messages=[
        {
            'role': 'system',
            'content': 'You are a friendly tavern keeper NPC in a fantasy game. Keep responses short (2-3 sentences).'
        },
        {
            'role': 'user',
            'content': 'Hello, what do you sell?'
        }
    ]
)

print(response['message']['content'])
