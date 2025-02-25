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

MODEL="deepseek-chat"
def generate_client(api_key):
	return OpenAI(
	  base_url="https://api.deepseek.com",
	  api_key=api_key,
	)

system_message = "Bạn là một người hỗi trợ cho một công ty Thương Mại Điện Tử gọi là CycleAI"
system_message += "Giải thích ngắn gọn, câu trả lời lịch sự, không hơn 1 câu"
system_message += "Luôn luôn chính xác. Nếu bạn không biết câu trả lời, hãy nói tôi không biết"


policy = {"sản phẩm bị cấm và Sản phẩm không được hỗ trợ":"Thuốc kê đơn và các sản phẩm tăng cường sinh lý, sản phẩm nguy hiểm và độc hại, bao gồm súng và vũ khí,Thuốc lá và ma túy","sản phẩm bị hạn chế":"Sữa công thức và Sữa tăng trưởng dành cho trẻ sơ sinh (Bị cấm)Người dùng không được phép quảng bá bất kỳ nội dung nào liên quan đến sản phẩm bị hạn chế nếu Nhà bán hàng chưa được duyệt để thực hiện. Một số sản phẩm bị hạn chế chỉ có thể được quảng bá khi có sự phê duyệt bổ sung","giới hạn về cách quảng bá sản phẩm":"Hoạt động bất hợp pháp hoặc tội phạm,Vi phạm quyền sở hữu trí tuệ,Nội dung cờ bạc"}

def get_policy(user_policy):
	print(f"Đây là tool check VPCS cho {policy}")
	CS = user_policy.lower()
	return policy.get(CS,"Không tồn tại")


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
def handle_tool_call(message):
	tool_call = message.tool_calls[0]
	arguments  = json.loads(tool_call.function.arguments)
	print(f"The arguments {arguments}")
	policy = arguments.get('policy')
	print(f"In the handle tool call function the policy {policy}")
	info = get_policy(policy),
	response = {
		"role": "tool",
		"content": json.dumps({"policy":policy,"information": info}),
		"tool_call_id": tool_call.id
	}
	return response, policy

deepseek_client=generate_client(DEEPSEEK_API)
def chat(message, history):
	messages = [{"role":"system", "content": system_message}] + history + [{"role": "user", "content":message}]
	response = deepseek_client.chat.completions.create(model=MODEL, messages = messages, tools = tools)

	if response.choices[0].finish_reason == "tool_calls":
		print(f"In the Chat function {response}")
		message = response.choices[0].message
		response, city = handle_tool_call(message)
		messages.append(message)
		messages.append(response)
		response = deepseek_client.chat.completions.create(model = MODEL, messages = messages)
	try:
		return response.choices[0].message.content
	except Exception as e:
		raise e
	finally :
		print(response.choices[0].message.content)

def main():
	result =chat(input("Text here"))
	print(result)

if "__name__"=="main":
	main()