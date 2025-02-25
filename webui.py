import gradio as gr

import ecomchat as ecom


gr.ChatInterface(ecom.chat, type = "messages").launch()