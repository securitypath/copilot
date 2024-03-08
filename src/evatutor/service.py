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

llm = ChatOpenAI(temperature=1.0, model='gpt-4-turbo-preview')


def predict(history, user_prompt, user_selection, system_prompt):
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history = history + [["Sistema: "+prompts[system_prompt][2] + "\n Usuario: " + user_prompt + "\n Codigo/Pregunta seleccionados: " + user_selection, ""]]
    history_langchain_format.append(HumanMessage(content=history[-1][0]))
    gpt_response = llm(history_langchain_format)
    history[-1][1] = gpt_response.content
    return system_prompt, history


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
  const currentUserSelection = document.getSelection();
  if (currentUserSelection) {
  document.getElementById("evatutor_user_selection").children[0].children[1].value = currentUserSelection;
    document.getElementById("evatutor_user_selection").children[0].children[1]
         .dispatchEvent(new Event('input', { detail: { value: currentUserSelection } }));
  }
});
})""") as demo:
    system_prompt = gr.State(0)

    choice = gr.Dropdown(list(map(lambda prompt: prompt[0], prompts)), type="index", label="Contexto del agente",
                         info="Busca el agente que mejor se adapte a tus dudas.", value=0)

    description = gr.Textbox(lines=2, visible=False, interactive=False, show_copy_button=True)


    def show_description(X):
        return gr.Textbox(label="Descripción", value=prompts[X][1], lines=2, visible=True, interactive=False,
                          show_copy_button=True)


    choice.input(show_description, inputs=choice, outputs=description)

    chatbot = gr.Chatbot(visible=False)
    chatbot.like(vote, None, None)
    user_prompt = gr.Textbox(label="Tu mensaje:", visible=False)
    chat = gr.Button(value="Enviar", visible=False)
    user_selection = gr.Textbox(label="Tu duda es sobre:", visible=False, interactive=False,
                                elem_id='evatutor_user_selection')

    chat.click(predict, inputs=[chatbot, user_prompt, user_selection, system_prompt], outputs=[system_prompt, chatbot])
    user_prompt.submit(predict, inputs=[chatbot, user_prompt, user_selection, system_prompt], outputs=[system_prompt, chatbot])

    def confirm(prompt_choice, index):
        print(prompt_choice)
        return gr.Dropdown(choices=[], visible=False), gr.Textbox(visible=False), gr.Chatbot([], elem_id="chatbot",
                                                                                 bubble_full_width=True,
                                                                                 show_label=False,
                                                                                 visible=True), gr.Textbox(
            label="Tu mensaje:", visible=True, interactive=True), gr.Button(value="Enviar", visible=True), gr.Button(
            value="Confirmar", visible=False), prompt_choice


    confirm_prompt = gr.Button(value="Confirmar prompt")
    confirm_prompt.click(confirm, inputs=[choice, system_prompt],
                         outputs=[choice, description, chatbot, user_prompt, chat, confirm_prompt, system_prompt])

demo.queue()
demo.launch(share=False)
