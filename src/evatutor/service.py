import json
import gradio as gr
import time

def load_json(path):
    with open(path) as file:
        return json.load(file)

prompts = load_json("./prompts.json")

def add_text(history, text, choice):
    history = history + [(text, None)]
    return history, gr.Textbox(value="", interactive=False)


def add_file(history, file):
    history = history + [((file.name,), None)]
    return history




def bot(history):
    response = "**That's cool!**"
    history[-1][1] = ""
    for character in response:
        history[-1][1] += character
        time.sleep(0.05)
        yield history


with gr.Blocks(title="Evatutor", css="footer{display:none !important}") as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot", bubble_full_width=True, show_label=False)

    choice = gr.Dropdown(list(map(lambda prompt: prompt[0], prompts)), type="index", label="Agent Context",
                         info="Modify the context of your agent to enhance its helpfulness.")

    txt = gr.Textbox(scale=4, show_label=False, placeholder="Enter text and press enter", container=False)

    txt_msg = txt.submit(add_text, [chatbot, txt, choice], [chatbot, txt], queue=False).then(bot, chatbot, chatbot,
                                                                                             api_name="bot_response")
    txt_msg.then(lambda: gr.Textbox(interactive=True), None, [txt], queue=False)


demo.queue()
demo.launch()
