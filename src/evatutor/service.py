import json
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
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

llm = ChatOpenAI(temperature=1.0, model='gpt-3.5-turbo-0613')


def predict(history, choice, user_prompt, user_selection):
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history = history + [[prompts[choice][1] + "\n Usuario: " + "" + "\n Codigo/Pregunta: " + user_selection, ""]]
    history_langchain_format.append(HumanMessage(content=history[-1][0]))
    gpt_response = llm(history_langchain_format)
    history[-1][1] = gpt_response.content
    return history


def add_file(history, file):
    history = history + [((file.name,), None)]
    return history


def vote(data: gr.LikeData):
    if data.liked:
        print("You upvoted this response: " + data.value)
    else:
        print("You downvoted this response: " + data.value)


with gr.Blocks(title="Evatutor", css="footer{display:none !important} .chatbot {bottom: 12em!important;}", js="""(() => {
document.addEventListener("selectionchange", () => {
  const currentUserSelection = document.getSelection().toString();
  if (currentUserSelection) {
  document.getElementById("evatutor_user_selection").children[0].children[1].value = currentUserSelection;
    document.getElementById("evatutor_user_selection").children[0].children[1]
         .dispatchEvent(new Event('input', { detail: { value: currentUserSelection } }));
  }
});
})""") as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot", bubble_full_width=True, show_label=False)

    choice = gr.Dropdown(list(map(lambda prompt: prompt[0], prompts)), type="index", label="Contexto del agente",
                         info="Busca el agente que mejor se adapte a tus dudas.")

    user_selection = gr.Textbox(label="Tu duda es sobre:", visible=False, interactive=False, elem_id='evatutor_user_selection')

    # user_prompt = gr.Textbox(label="Tu mensaje:")

    btn = gr.Button(value="Enviar")
    btn.click(predict, inputs=[chatbot, choice, user_selection], outputs=[chatbot])

    chatbot.like(vote, None, None)

demo.queue()
demo.launch(share=True)
