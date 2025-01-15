from fastapi import FastAPI, Request
import gradio as gr
import time
from supabase import create_client, Client, ClientOptions, AuthSessionMissingError
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os



app = FastAPI()
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")


def get_user(request: Request):
    authorization = request.headers.get("Authorization")
    if authorization is None:
        return False
    supabase: Client = create_client(
              supabase_url,
              supabase_key,
              ClientOptions(
                  headers = {
                    "Authorization": authorization
                  },
                  auto_refresh_token=False
              )
    )
    token = authorization.replace("Bearer ", "")
    return supabase.auth.set_session(token, "")


model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

system_message = """
You are a highly knowledgeable Cybersecurity Expert with knowledge in SQL and Risk managment. Your primary goal is to assist CISOs and system administrators with their security-related inquiries. Please adhere to the following guidelines in your responses:

1. **Expertise & Accuracy**: Provide correct, in-depth, and technically accurate solutions grounded in established cybersecurity principles, standards (such as NIST, ISO, CIS Controls), and best practices.

2. **Clarity & Structure**: Present answers clearly and concisely. When appropriate, use bullet points, step-by-step instructions, code snippets, or configuration examples to make your guidance easy to follow.

3. **Proactive Guidance**: If a question is ambiguous or lacks details, ask clarifying questions before offering a solution. If multiple solutions exist, highlight potential trade-offs and recommend best practices.

4. **References & Context**: Where applicable, include links or references to authoritative resources (e.g., official documentation, white papers) that can help the user dive deeper.

5. **Respect Boundaries**: If a user’s question goes beyond your training or pertains to malicious or unethical use of cybersecurity tactics, politely decline or refocus the conversation on legitimate cybersecurity practices.

Your role is to provide expert cybersecurity support to help CISOs and sysadmins make informed decisions and solve their real-world security problems. 

"""

def predict(message, history):
    history_langchain_format = []
    if len(history) == 0:
        history_langchain_format.append(SystemMessage(content=system_message))
    for msg in history:
        if msg['role'] == "user":
            history_langchain_format.append(HumanMessage(content=msg['content']))
        elif msg['role'] == "assistant":
            history_langchain_format.append(AIMessage(content=msg['content']))
    history_langchain_format.append(HumanMessage(content=message))
    gpt_response = model.invoke(history_langchain_format)
    return gpt_response.content



demo = gr.ChatInterface(
    predict,
    chatbot=gr.Chatbot(label=False),
    type="messages",
    editable=True,
    save_history=True,
    fill_width=True,
    fill_height=True,
    css="""
footer{display:none !important}
.dark  {
    --body-background-fill: rgb(18, 18, 18);
}
.gradio-container {
  border: 0 !important;
}
    """
)


app = gr.mount_gradio_app(app, demo, path="/", auth_dependency=get_user)


if __name__ == '__main__':
    uvicorn.run(app)
