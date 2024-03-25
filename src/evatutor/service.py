import json

import gradio as gr
from gradio import Button
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage


def load_json(path):
    with open(path) as file:
        return json.load(file)


class DummyAI:
    def __init__(self):
        self.content = "Yes"

    def __call__(self, *args, **kwargs):
        return self


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

    def predict(self, message, history, system_prompt_id, user_selection, prompt_description):
        history_langchain_format = []
        for human, ai in history:
            history_langchain_format.append(HumanMessage(content=self.valid_user_message(human)))
            history_langchain_format.append(AIMessage(content=ai))

        history_langchain_format.append(SystemMessage(content=self.prompts[system_prompt_id][Prompt.PROMPT_SYSTEM]))
        history_langchain_format.append(HumanMessage(content=self.valid_user_message(message)))
        history_langchain_format.append(HumanMessage(content="User selection: " + user_selection))
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


evatutor = Evatutor(llm=ChatOpenAI(temperature=1.0, model='gpt-4-turbo-preview'), prompts=load_json("./prompts.json"))

with gr.Blocks(css="footer{display:none !important}", js="""(() => {
          document.addEventListener("selectionchange", () => {
            const currentUserSelection = document.getSelection();
            if (currentUserSelection) {
            document.getElementById("evatutor_user_selection").children[0].children[1].value = currentUserSelection;
              document.getElementById("evatutor_user_selection").children[0].children[1]
                   .dispatchEvent(new Event('input', { detail: { value: currentUserSelection } }));
            }
          });
          })""") as demo:
    system_prompt_id = gr.Dropdown(evatutor.prompt_titles, type="index",
                                   label="¿Cómo quieres que EvaTutor se comparte?",
                                   info="Busca el agente que mejor se adapte a tus dudas.",
                                   value=evatutor.default_prompt, allow_custom_value=True, render=False)

    description = gr.Textbox(value=evatutor.default_prompt_description, label="Descripción", interactive=False,
                             render=False)

    chat_interface = gr.ChatInterface(evatutor.predict,
                                      retry_btn=Button(value="🔄", variant="secondary", scale=0.1, min_width=1,
                                                       render=False),
                                      clear_btn=Button(value="🗑️", variant="secondary", scale=0.1, min_width=1,
                                                       render=False),
                                      undo_btn=Button(value="↩️️", variant="secondary", scale=0.1, min_width=1,
                                                      render=False), submit_btn="📨",
                                      chatbot=gr.Chatbot(value=evatutor.load_initial_message(), label="EvaTutor",
                                                         scale=1, show_label=False, latex_delimiters=[
                                              {"left": "$", "right": "$", "display": False},
                                              {"left": "[", "right": "]", "display": False}
                                          ], render=False),
                                      additional_inputs=[system_prompt_id, description,
                                                         gr.Textbox(label="Tu duda es sobre:", visible=False,
                                                                    interactive=False,
                                                                    elem_id='evatutor_user_selection')]
                                     )

    system_prompt_id.change(evatutor.change_system_prompt, system_prompt_id,
                            [chat_interface.chatbot, chat_interface.chatbot_state, chat_interface.saved_input,
                             description], queue=False, show_api=False)

demo.queue()
demo.launch(share=False)
