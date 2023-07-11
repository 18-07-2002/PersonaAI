import gradio as gr
import os
import json
import requests

# Streaming endpoint
API_URL = "https://api.openai.com/v1/chat/completions"  # os.getenv("API_URL") + "/generate_stream"


# Inferenece function
def predict(
    openai_api_key,
    system_msg,
    inputs,
    top_p,
    temperature,
    chat_counter,
    chatbot=[],
    history=[],
):
    # headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": f"Bearer {openai_api_key}"
    # }
    headers ={}

    print(f"system message is ^^ {system_msg}")
    if system_msg.strip() == "":
        initial_message = [
            {"role": "user", "content": f"{inputs}"},
        ]
        multi_turn_message = []
    else:
        initial_message = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"{inputs}"},
        ]
        multi_turn_message = [
            {"role": "system", "content": system_msg},
        ]

    if chat_counter == 0:
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": initial_message,
            "temperature": 1.0,
            "top_p": 1.0,
            "n": 1,
            "stream": True,
            "presence_penalty": 0,
            "frequency_penalty": 0,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        }

        print(f"chat_counter - {chat_counter}")
    else:  # if chat_counter != 0 :
        messages = multi_turn_message
        for data in chatbot:
            user = {}
            user["role"] = "user"
            user["content"] = data[0]
            assistant = {}
            assistant["role"] = "assistant"
            assistant["content"] = data[1]
            messages.append(user)
            messages.append(assistant)
        temp = {}
        temp["role"] = "user"
        temp["content"] = inputs
        messages.append(temp)

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "n": 1,
            "stream": True,
            "presence_penalty": 0,
            "frequency_penalty": 0,
        }

    chat_counter += 1
    history.append(inputs)
    print(f"Logging : payload is - {payload}")
    # make a POST request to the API endpoint using the requests.post method, passing in stream=True

    response = requests.post(API_URL, headers=headers, json=payload, stream=True)

    token_counter = 0
    partial_words = ""

    counter = 0
    for chunk in response.iter_lines():
        # Skipping first chunk
        if counter == 0:
            counter += 1
            continue
        # counter+=1
        # check whether each line is non-empty
        if chunk.decode():
            chunk = chunk.decode()
            # decode each line as response data is in bytes
            if (
                len(chunk) > 12
                and "content" in json.loads(chunk[6:])["choices"][0]["delta"]
            ):
                # if len(json.loads(chunk.decode()[6:])['choices'][0]["delta"]) == 0:
                #  break
                partial_words = (
                    partial_words
                    + json.loads(chunk[6:])["choices"][0]["delta"]["content"]
                )
                if token_counter == 0:
                    history.append(" " + partial_words)
                else:
                    history[-1] = partial_words
                chat = [
                    (history[i], history[i + 1]) for i in range(0, len(history) - 1, 2)
                ]  # convert to tuples of list
                token_counter += 1
                yield chat, history, chat_counter, response  # resembles {chatbot: chat, state: history}


# # Check if the request was successful
# if response.status_code == 200:
#     token_counter = 0
#     partial_words = ""

#     counter = 0
#     for chunk in response.iter_lines():
#         # Skipping first chunk
#         if counter == 0:
#             counter += 1
#             continue

#         # check whether each line is non-empty
#         if chunk:
#             chunk = chunk.decode()

#             try:
#                 json_data = json.loads(chunk)
#                 if (
#                     len(json_data["choices"]) > 0
#                     and "content" in json_data["choices"][0]["message"]
#                 ):
#                     partial_words = (
#                         partial_words
#                         + json_data["choices"][0]["message"]["content"]
#                     )
#                     if token_counter == 0:
#                         history.append(" " + partial_words)
#                     else:
#                         history[-1] = partial_words
#                     chat = [
#                         (history[i], history[i + 1])
#                         for i in range(0, len(history) - 1, 2)
#                     ]
#                     token_counter += 1
#                     yield chat, history, chat_counter, response
#             except json.decoder.JSONDecodeError as e:
#                 print(f"Error decoding JSON: {e}")
#                 # Handle the JSON decoding error
#                 error_message = f"Error decoding JSON: {e}"
#                 raise ValueError(error_message)
# else:
#     print(f"Error: Request failed with status code {response.status_code}")
#     response.raise_for_status()


# Resetting to blank
def reset_textbox():
    return gr.update(value="")


# to set a component as visible=False
def set_visible_false():
    return gr.update(visible=False)


# to set a component as visible=True
def set_visible_true():
    return gr.update(visible=True)

# logo_html = gr.HTML('<img src="logo.png" alt="Logo">')

title = """<h1 align="center" style="color: orange; font-size: 55px;font-family: Arial, sans-serif;font-weight: bold;">PersonaAI</h1>"""


description = """<center>🌟Developed by Swayam Arunav, NIT Rourkela. To report any issue contact me at <a href="mailto:khuntiaswayam@gmail.com" style="color: black; font-weight: bold; background-color: white;">GMAIL</a> or <a href="https://wa.me/7326828328" style="color: black; font-weight: bold; background-color: white;">WhatsApp</a></center>"""


# Using info to add additional information about System message in GPT
system_msg_info = """A conversation could begin with a system message to gently instruct the assistant. 
System message helps set the behaviour of the AI Assistant. For example, the assistant could be instructed with 'You are a helpful assistant.'"""

# Modifying existing Gradio Theme
theme = gr.themes.Soft(
    primary_hue="orange",
    secondary_hue="slate",
    neutral_hue="slate",
    text_size=gr.themes.sizes.text_lg,
)

with gr.Blocks(
    css="""#col_container { margin-left: auto; margin-right: auto;} #chatbot {height: 520px; overflow: auto;}""",
    theme=theme,
) as demo:
    # gr.HTML(logo_html)
    gr.HTML(title)
    gr.HTML(
        """<h3 align="center">🔥This Web-app provides you access to GPT4 and GPT3.5-turbo Model with System Messages. Please note that you would be needing an OPENAI API key for the access🙌</h1>"""
    )
    gr.HTML(description)
    gr.HTML("""<center><a href=</center>""")

    with gr.Column(elem_id="col_container"):
        # Users need to provide their own GPT API key, it is no longer provided by Huggingface
        with gr.Row():
            openai_api_key = gr.Textbox(
                label="OpenAI API Key",
                value="",
                type="password",
                placeholder="sk..",
                info="You have to provide your own OPENAI API keys for this app to function properly",
            )
            with gr.Accordion(label="System message:", open=False):
                system_msg = gr.Textbox(
                    label="Instruct the AI Assistant to set its role",
                    info=system_msg_info,
                    value="",
                    placeholder="Type here..",
                )
                accordion_msg = gr.HTML(
                    value="🚧 To set System message you will have to refresh the app",
                    visible=False,
                )

        chatbot = gr.Chatbot(label="Jessica", elem_id="chatbot")
        inputs = gr.Textbox(
            placeholder="Hi there!", label="Type an input and press Enter"
        )
        state = gr.State([])
        with gr.Row():
            with gr.Column(scale=7):
                b1 = gr.Button().style(scale=1)
            with gr.Column(scale=3):
                server_status_code = gr.Textbox(
                    label="Status code from OpenAI server",
                )

        # top_p, temperature
        with gr.Accordion("Parameters", open=False):
            top_p = gr.Slider(
                minimum=-0,
                maximum=1.0,
                value=1.0,
                step=0.05,
                interactive=True,
                label="Top-p (nucleus sampling)",
            )
            temperature = gr.Slider(
                minimum=-0,
                maximum=5.0,
                value=1.0,
                step=0.1,
                interactive=True,
                label="Temperature",
            )
            chat_counter = gr.Number(value=0, visible=False, precision=0)

    # Event handling
    inputs.submit(
        predict,
        [
            openai_api_key,
            system_msg,
            inputs,
            top_p,
            temperature,
            chat_counter,
            chatbot,
            state,
        ],
        [chatbot, state, chat_counter, server_status_code],
    )  # openai_api_key
    b1.click(
        predict,
        [
            openai_api_key,
            system_msg,
            inputs,
            top_p,
            temperature,
            chat_counter,
            chatbot,
            state,
        ],
        [chatbot, state, chat_counter, server_status_code],
    )  # openai_api_key

    inputs.submit(set_visible_false, [], [system_msg])
    b1.click(set_visible_false, [], [system_msg])
    inputs.submit(set_visible_true, [], [accordion_msg])
    b1.click(set_visible_true, [], [accordion_msg])

    b1.click(reset_textbox, [], [inputs])
    inputs.submit(reset_textbox, [], [inputs])

    # Examples
    with gr.Accordion(label="Examples for System message:", open=False):
        gr.Examples(
            examples=[
                [
                    """You are an AI programming assistant.
        
                - Follow the user's requirements carefully and to the letter.
                - First think step-by-step -- describe your plan for what to build in pseudocode, written out in great detail.
                - Then output the code in a single code block.
                - Minimize any other prose."""
                ],
                [
                    """You are ComedianGPT who is a helpful assistant. You answer everything with a joke and witty replies."""
                ],
                [
                    "You are ChefGPT, a helpful assistant who answers questions with culinary expertise and a pinch of humor."
                ],
                [
                    "You are FitnessGuruGPT, a fitness expert who shares workout tips and motivation with a playful twist."
                ],
                [
                    "You are SciFiGPT, an AI assistant who discusses science fiction topics with a blend of knowledge and wit."
                ],
                [
                    "You are PhilosopherGPT, a thoughtful assistant who responds to inquiries with philosophical insights and a touch of humor."
                ],
                [
                    "You are EcoWarriorGPT, a helpful assistant who shares environment-friendly advice with a lighthearted approach."
                ],
                [
                    "You are MusicMaestroGPT, a knowledgeable AI who discusses music and its history with a mix of facts and playful banter."
                ],
                [
                    "You are SportsFanGPT, an enthusiastic assistant who talks about sports and shares amusing anecdotes."
                ],
                [
                    "You are TechWhizGPT, a tech-savvy AI who can help users troubleshoot issues and answer questions with a dash of humor."
                ],
                [
                    "You are FashionistaGPT, an AI fashion expert who shares style advice and trends with a sprinkle of wit."
                ],
                [
                    "You are ArtConnoisseurGPT, an AI assistant who discusses art and its history with a blend of knowledge and playful commentary."
                ],
                [
                    "You are a helpful assistant that provides detailed and accurate information."
                ],
                ["You are an assistant that speaks like Shakespeare."],
                ["You are a friendly assistant who uses casual language and humor."],
                [
                    "You are a financial advisor who gives expert advice on investments and budgeting."
                ],
                [
                    "You are a health and fitness expert who provides advice on nutrition and exercise."
                ],
                [
                    "You are a travel consultant who offers recommendations for destinations, accommodations, and attractions."
                ],
                [
                    "You are a movie critic who shares insightful opinions on films and their themes."
                ],
                [
                    "You are a history enthusiast who loves to discuss historical events and figures."
                ],
                [
                    "You are a tech-savvy assistant who can help users troubleshoot issues and answer questions about gadgets and software."
                ],
                [
                    "You are an AI poet who can compose creative and evocative poems on any given topic."
                ],
            ],
            inputs=system_msg,
        )

# demo.queue(max_size=99, concurrency_count=20).launch(debug=True)
demo.queue().launch(debug=True)
