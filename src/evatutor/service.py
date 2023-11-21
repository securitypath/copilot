import json
from threading import Thread

import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList, \
    TextIteratorStreamer

tokenizer = AutoTokenizer.from_pretrained("togethercomputer/RedPajama-INCITE-Chat-3B-v1")
model = AutoModelForCausalLM.from_pretrained("togethercomputer/RedPajama-INCITE-Chat-3B-v1", torch_dtype=torch.float16)
model = model.to('cuda:0')


class StopOnTokens(StoppingCriteria):
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        stop_ids = [29, 0]
        for stop_id in stop_ids:
            if input_ids[0][-1] == stop_id:
                return True
        return False


def bot(history_transformer_format):
    history_transformer_format[-1][1] = ""
    stop = StopOnTokens()

    messages = "".join(["".join(["\n<human>:" + item[0], "\n<bot>:" + item[1]])  # curr_system_message +
                        for item in history_transformer_format])

    model_inputs = tokenizer([messages], return_tensors="pt").to("cuda")
    streamer = TextIteratorStreamer(tokenizer, timeout=10., skip_prompt=True, skip_special_tokens=True)
    generate_kwargs = dict(
        model_inputs,
        streamer=streamer,
        max_new_tokens=1024,
        do_sample=True,
        top_p=0.95,
        top_k=1000,
        temperature=1.0,
        num_beams=1,
        stopping_criteria=StoppingCriteriaList([stop])
    )
    t = Thread(target=model.generate, kwargs=generate_kwargs)
    t.start()

    for new_token in streamer:
        if new_token != '<':
            history_transformer_format[-1][1] += new_token
            yield history_transformer_format


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


def vote(data: gr.LikeData):
    if data.liked:
        print("You upvoted this response: " + data.value)
    else:
        print("You downvoted this response: " + data.value)


with gr.Blocks(title="Evatutor", css="footer{display:none !important}") as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot", bubble_full_width=True, show_label=False)

    choice = gr.Dropdown(list(map(lambda prompt: prompt[0], prompts)), type="index", label="Agent Context",
                         info="Modify the context of your agent to enhance its helpfulness.")

    txt = gr.Textbox(scale=4, show_label=False, placeholder="Enter text and press enter", container=False)

    txt_msg = txt.submit(add_text, [chatbot, txt, choice], [chatbot, txt], queue=False).then(bot, chatbot, chatbot,
                                                                                             api_name="bot_response")
    txt_msg.then(lambda: gr.Textbox(interactive=True), None, [txt], queue=False)

    chatbot.like(vote, None, None)


demo.queue()
demo.launch()
