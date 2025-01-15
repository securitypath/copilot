FROM python:3.10-slim

WORKDIR /usr/src/app
RUN pip install gradio gradio_client fastapi[standard] supabase
RUN pip install --upgrade --quiet  langchain-huggingface text-generation transformers google-search-results numexpr langchainhub sentencepiece jinja2 bitsandbytes accelerate langchain-core langgraph>0.2.27
RUN pip install -qU langchain-google-genai
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"
COPY . .

CMD ["fastapi", "run", "src/evatutor/webapp.py", "--port", "7860"]
