import getpass
import os

if not os.environ.get("OPENAI_API_KEY"):
	os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from langchain.chat_models import init_chat_model

llm = init_chat_model("gpt-4o-mini", model_provider="openai")

try:
	response = llm.invoke("What is the capital of India?")
	print("Response:", response)
except Exception as e:
	print("Error connecting to OPENAI API:", e)
	print("Please check your internet connection, firewall settings, and API key.")
print("llm:", llm)


