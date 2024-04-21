import json

import gradio as gr
from gradio import Button
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import pathlib

app_path = str(pathlib.Path(__file__).parent.resolve())


def load_json(path):
    with open(path) as file:
        return json.load(file)


class DummyAI:
    def __init__(self, temperature=0.6, model='gpt-4-turbo-preview'):
        self.content = "Yes"

    def __call__(self, *args, **kwargs):
        return self

    def stream(self, x):
        yield self


class Prompt:
    TITLE = 0
    DESCRIPTION = 1
    PROMPT_SYSTEM = 2


class Evatutor:
    def __init__(self, llm, prompts):
        self.llm = llm
        self.prompts = prompts
        self.default_prompt = 0
        self.prompt_titles = list(map(lambda prompt: prompt[self.default_prompt], prompts))
        self.default_prompt_description = self.prompts[self.default_prompt][Prompt.DESCRIPTION]

    @staticmethod
    def valid_user_message(message):
        return "" if message is None else message

    def predict(self, message, history, system_prompt_id, prompt_description):
        history_langchain_format = []
        for human, ai in history:
            history_langchain_format.append(HumanMessage(content=self.valid_user_message(human)))
            history_langchain_format.append(AIMessage(content=ai))
        history_langchain_format.append(SystemMessage(content=self.prompts[system_prompt_id][Prompt.PROMPT_SYSTEM]))
        if message is not None:
            history_langchain_format.append(HumanMessage(content=message))
        partial_message = ""
        for chunk in self.llm.stream(history_langchain_format):
            partial_message += chunk.content
            yield partial_message

    @staticmethod
    def add_file(history, file):
        history = history + [((file.name,), None)]
        return history

    @staticmethod
    def vote(data):
        if data.liked:
            print("You upvoted this response: " + data.value)
        else:
            print("You downvoted this response: " + data.value)

    def load_initial_message(self, system_prompt_id=0):
        history = [SystemMessage(content=self.prompts[system_prompt_id][Prompt.PROMPT_SYSTEM])]
        gpt_response = self.llm(history)
        return [[None, gpt_response.content]]

    def change_system_prompt(self, system_prompt_id=0):
        return self.load_initial_message(system_prompt_id), [], None, self.prompts[system_prompt_id][Prompt.DESCRIPTION]


evatutor = Evatutor(llm=ChatOpenAI(temperature=0.7, model='gpt-4-turbo-preview'), prompts=load_json(app_path+"/prompts.json"))

with gr.Blocks(css="""
footer{display:none !important}
.dark  {
    --body-background-fill: rgb(18, 18, 18);
}
.gradio-container {
  border: 0 !important;
}
""", js="""(() => {
     document.addEventListener('ai_explain', (event) => {
            document.dispatchEvent(new CustomEvent(event.detail.id, {
                detail: true
            }));
           document.getElementById("evatutor_user_prompt").getElementsByTagName('textarea')[0].value = event.detail.payload;
           document.getElementById("evatutor_user_prompt").getElementsByTagName('textarea')[0].dispatchEvent(new Event('input'));
           document.getElementById("evatutor_submit_button").click()
    });  
})""") as webapp:
    system_prompt_id = gr.Dropdown(evatutor.prompt_titles, type="index",
                                   label="¿Cómo quieres que EvaTutor se comparte?",
                                   info="Busca el agente que mejor se adapte a tus dudas.",
                                   value=evatutor.default_prompt, allow_custom_value=True, render=False)

    description = gr.Textbox(value=evatutor.default_prompt_description, label="Descripción", interactive=False,
                             render=False)

    prompt = gr.Textbox(
        render=False,
        show_label=False,
        label="Message",
        placeholder="Type a message...",
        elem_id='evatutor_user_prompt',
        scale=7,
        autofocus=True,
    )

    chat_interface = gr.ChatInterface(evatutor.predict,
                                      textbox=prompt,
                                      retry_btn=Button(value="🔄", variant="secondary", scale=1, min_width=1,
                                                       render=False),
                                      clear_btn=Button(value="🗑️", variant="secondary", scale=1, min_width=1,
                                                       render=False),
                                      undo_btn=Button(value="↩️️", variant="secondary", scale=1, min_width=1,
                                                      render=False),
                                      submit_btn=Button(value="📨", variant="primary", scale=1, min_width=1,
                                                        render=False, elem_id="evatutor_submit_button"),
                                      chatbot=gr.Chatbot(value=evatutor.load_initial_message(), label="EvaTutor",
                                                         scale=1, show_label=False, latex_delimiters=[
                                              {"left": "$", "right": "$", "display": False},
                                              {"left": "[", "right": "]", "display": False}
                                          ], render=False),
                                      additional_inputs=[system_prompt_id, description]
                                      )

    system_prompt_id.change(evatutor.change_system_prompt, system_prompt_id,
                            [chat_interface.chatbot, chat_interface.chatbot_state, chat_interface.saved_input,
                             description], queue=False, show_api=False)

