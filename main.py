import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

load_dotenv()

DEEPSEEK_API = os.getenv("DEEPSEEK_API_KEY")




if DEEPSEEK_API :
	print("API KEY exists")
else:
	print("API KEY not set")

MODEL ="deepseek/deepseek-r1:free"
def generate_client(api_key):
	return OpenAI(
	  base_url="https://openrouter.ai/api/v1",
	  api_key=api_key,
	)

system_message = "Bạn là một người hỗi trợ cho một công ty Thương Mại Điện Tử gọi là CycleAI"
system_message += "Giải thích ngắn gọn, câu trả lời lịch sự, không hơn 1 câu"
system_message += "Luôn luôn chính xác. Nếu bạn không biết câu trả lời, hãy nói tôi không biết"


policy = {"sản phẩm bị cấm và Sản phẩm không được hỗ trợ":"Thuốc kê đơn và các sản phẩm tăng cường sinh lý, sản phẩm nguy hiểm và độc hại, bao gồm súng và vũ khí,Thuốc lá và ma túy","sản phẩm bị hạn chế":"Sữa công thức và Sữa tăng trưởng dành cho trẻ sơ sinh (Bị cấm)Người dùng không được phép quảng bá bất kỳ nội dung nào liên quan đến sản phẩm bị hạn chế nếu Nhà bán hàng chưa được duyệt để thực hiện. Một số sản phẩm bị hạn chế chỉ có thể được quảng bá khi có sự phê duyệt bổ sung","giới hạn về cách quảng bá sản phẩm":"Hoạt động bất hợp pháp hoặc tội phạm,Vi phạm quyền sở hữu trí tuệ,Nội dung cờ bạc"}

def get_policy(policy):
	print(f"Đây là tool check VPCS cho {policy}")
	CS = policy.lower()
	return policy.get(policy,"Không tồn tại")


policy_function = {
	"name" : "get_policy",
	"description": "Nhận lại những thông tin về chính sách được trả lại, ví dụ khi một khách hàng hỏi 'Chính sách của những sản phẩm bị cấm và không được hỗi trợ'",
	"parameters": {
		"type": "object",
		"properties": {
			"policy": {
			"type": "string",
			"description": "Thông tin về chính sách mà khách hàng muốn truy xuất"
			},

		},
		"required":["policy"],
		"additionalProperties": False
	}
}

# Included in a list of tools:
tools = [{"type": "function", "function": policy_function}]
MODEL="deepseek-chat"
def handle_tool_call(message):
	tool_call = message.tool_calls[0]
	arguments  = json.loads(tool_call.function.arguments)
	policy = arguments.get('policy'),
	info = get_policy(policy),
	response = {
		"role": "tool",
		"content": json.dumps({"policy":policy,"information": info}),
		"tool_call_id": tool_call.id
	}
	return response, policy


def chat(message, history):
	messages = [{"role":"system", "content": system_message}] + history + [{"role": "user", "content":message}]
	response = openai.chat.completions.create(model=MODEL, messages = messages, tools = tools)

	if response.choice[0].finish_reason == "tool_calls":
		message = response.choices[0].message
		response, city = handle_tool_call(message)
		messages.append(message)
		messages.append(repsonse)
		response = openai.chat.completions.create(model = MODEL, messages = messages)

	try:
		return response.choices[0].message.content
	except Exception as e:
		raise e
	finally :
		print(response.choices[0].message.content)

