import json

from gradio import Chatbot, Button
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import gradio as gr


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
llm.max_tokens = 100


def predict(message, history, system_prompt, user_selection):
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))

    history_langchain_format.append(SystemMessage(content=prompts[system_prompt][2]))
    history_langchain_format.append(HumanMessage(content=message))
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


demo = gr.ChatInterface(predict, retry_btn=Button(value="🔄", variant="secondary", scale=0.1, min_width=1),
    clear_btn=Button(value="🗑️", variant="secondary", scale=0.1, min_width=1),
    undo_btn=Button(value="↩️️", variant="secondary", scale=0.1, min_width=1),
    submit_btn="📨",
    chatbot=Chatbot(label="EvaTutor", scale=1, show_label=False,
        latex_delimiters=[{"left": "$", "right": "$", "display": False}]), css="footer{display:none !important}", js="""(() => {
       document.addEventListener("selectionchange", () => {
         const currentUserSelection = document.getSelection();
         if (currentUserSelection) {
         document.getElementById("evatutor_user_selection").children[0].children[1].value = currentUserSelection;
           document.getElementById("evatutor_user_selection").children[0].children[1]
                .dispatchEvent(new Event('input', { detail: { value: currentUserSelection } }));
         }
       });
       })""", additional_inputs=[gr.Dropdown(list(map(lambda prompt: prompt[0], prompts)), type="index",
                                             label="¿Cómo quieres que EvaTutor se comparte?",
                                             info="Busca el agente que mejor se adapte a tus dudas.", value=0, allow_custom_value=True),
        gr.Textbox(label="Tu duda es sobre:", visible=False, interactive=False, elem_id='evatutor_user_selection')],
    examples=[["¿Cómo empiezo?"], ["Ayúdame a resolver el siguiente problema: "],
              ["¿Qué es lo que me pide el problema?"]])

demo.queue()
demo.launch(share=False)
