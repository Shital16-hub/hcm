# test_azure_openai.py
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv(".env.local")

def test_azure_openai():
    try:
        llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("OPENAI_API_VERSION"),
            temperature=0.1,
        )
        
        response = llm.invoke("Hello, can you respond to test the connection?")
        print("✅ Azure OpenAI is working!")
        print(f"Response: {response.content}")
        
    except Exception as e:
        print(f"❌ Azure OpenAI Error: {e}")
        print("Check your .env.local file configuration")

if __name__ == "__main__":
    test_azure_openai()