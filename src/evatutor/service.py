import json

from gradio import Chatbot, Button
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import gradio as gr
import time


def bot(history_transformer_format):
    history_transformer_format[-1][1] = ""
    response = "Cool!"
    for new_token in response:
        history_transformer_format[-1][1] += new_token
        yield history_transformer_format


def load_json(path):
    with open(path) as file:
        return json.load(file)


prompts = load_json("./prompts.json")

llm = ChatOpenAI(temperature=1.0, model='gpt-4-turbo-preview')


def predict(message, history, system_prompt, user_selection, prompt_description):
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))

    history_langchain_format.append(SystemMessage(content=prompts[system_prompt][2]))
    history_langchain_format.append(HumanMessage(content=message))
    history_langchain_format.append(HumanMessage(content="User selection: "+user_selection))
    gpt_response = llm(history_langchain_format)
    return gpt_response.content


def add_file(history, file):
    history = history + [((file.name,), None)]
    return history


def vote(data: gr.LikeData):
    if data.liked:
        print("You upvoted this response: " + data.value)
    else:
        print("You downvoted this response: " + data.value)


def load_initial_message(system_prompt=0):
    history_langchain_format = []
    history_langchain_format.append(SystemMessage(content=prompts[system_prompt][2]))
    gpt_response = llm(history_langchain_format)
    return [[None, gpt_response.content]]


def change_system_prompt(system_prompt=0):
    return load_initial_message(system_prompt), [], None, prompts[system_prompt][1]


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
    system_prompt = gr.Dropdown(list(map(lambda prompt: prompt[0], prompts)), type="index",
                                label="¿Cómo quieres que EvaTutor se comparte?",
                                info="Busca el agente que mejor se adapte a tus dudas.", value=0,
                                allow_custom_value=True, render=False)

    description = gr.Textbox(value=prompts[0][1], label="Descripción", interactive=False, render=False)

    chat_interface = gr.ChatInterface(predict, retry_btn=Button(value="🔄", variant="secondary", scale=0.1, min_width=1,
                                                                render=False),
                                      clear_btn=Button(value="🗑️", variant="secondary", scale=0.1, min_width=1,
                                                       render=False),
                                      undo_btn=Button(value="↩️️", variant="secondary", scale=0.1, min_width=1,
                                                      render=False), submit_btn="📨",
                                      chatbot=gr.Chatbot(value=load_initial_message(), label="EvaTutor", scale=1,
                                                         show_label=False, latex_delimiters=[
                                              {"left": "$", "right": "$", "display": False}], render=False),
                                      additional_inputs=[system_prompt,description,
                                                         gr.Textbox(label="Tu duda es sobre:", visible=False,
                                                                    interactive=False,
                                                                    elem_id='evatutor_user_selection')],
                                      examples=[["¿Cómo empiezo?"], ["Ayúdame a resolver el siguiente problema: "],
                                                ["¿Qué es lo que me pide el problema?"]])

    system_prompt.change(change_system_prompt, system_prompt,
                         [chat_interface.chatbot, chat_interface.chatbot_state, chat_interface.saved_input, description],
                         queue=False, show_api=False)


demo.queue()
demo.launch(share=False)
