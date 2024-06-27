import openai
import pandas as pd
import halo
import json

def read_text_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {e}"
    
def decomposite_function(function):
    list_chat = []
    list_chat.append({"role": "system", "content": read_text_file("prompt_02.txt")})
    list_chat.append({"role": "user", "content": function})
    gptmodel = "gpt-4o"
    response = openai.ChatCompletion.create(model=gptmodel, messages=list_chat, timeout=120)
    content = response['choices'][0]['message']['content']
    json_start = content.find('{')
    json_end = content.rfind('}') + 1
    json_str = content[json_start:json_end]
    return  json.loads(json_str)

def decomposite_function_list(function_list):
    response_list = []
    for function in function_list:
        response_list.append(decomposite_function(function))
    return response_list

def extract_sub_functions(json_list):
    result = []
    for obj in json_list:
        if 'sub_functions' in obj:
            for sub_func in obj['sub_functions']:
                if 'sub_function' in sub_func and 'description' in sub_func:
                    result.append(f"{sub_func['sub_function']}：{sub_func['description']}")
    return result


def save_as_excel(json_data):
    rows = []
    for item in json_data:
        # original_functionの情報を取得
        original_function = item["original_function"]
        function = original_function["function"]
        function_description = original_function["description"]
        
        for sub_function in item["sub_functions"]:
            sub_function_name = sub_function["sub_function"]
            sub_function_description = sub_function["description"]
            mermaid_arrow = f"{function} --> {sub_function_name};"
            row = {
                "function": function,
                "function_description": function_description,
                "sub_function": sub_function_name,
                "sub_function_description": sub_function_description,
                "mermaid_arrow": mermaid_arrow
            }
            rows.append(row)

    # データフレームを作成
    df = pd.DataFrame(rows)

    # Excelファイルに書き込む
    df.to_excel(json_data[0]["original_function"]["function"] + ".xlsx", index=False)

def main():
    input_function = input("分解したい機能を入力してください：")
    input_num_process = input("階層を入力してください：")

    with halo.Halo(text='生成中...', spinner='dots'):
        temp_json = [decomposite_function(input_function)]
        whole_json = temp_json
        for i in range(int(input_num_process)-1):
            temp_json = decomposite_function_list(extract_sub_functions(temp_json))
            whole_json = whole_json + temp_json
            
    save_as_excel(whole_json)


if __name__ == "__main__":
    main()
    