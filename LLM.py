import dashscope
from dashscope import MultiModalConversation
from dashscope import Generation

def qwen_vlm_ocr_extract(img_path, api_key):
    """第一步：VLM-OCR 只提取试卷文字，不做任何分析"""
    dashscope.api_key = api_key
    messages = [
        {
            "role": "system",
            "content": [{"text": "仅提取图片全部文字，只返回识别原文"}]
        },
        {
            "role": "user",
            "content": [
                {"image": f"file://{img_path}"},
                {"text": "完整提取图片内所有文字"}
            ]
        }
    ]
    response = MultiModalConversation.call(
        model="qwen-vl-ocr",
        messages=messages
    )
    if response.status_code == 200:
        text = response.output.choices[0].message.content[0]["text"]
        print("===== OCR识别学生作答原文 =====")
        print(text)
        return text
    else:
        print(f"OCR调用失败！错误码：{response.code}, 错误信息：{response.message}")
        return None

def qwen_text_judge(student_text, standard_ans, total_score, api_key):
    """第二步：纯文本LLM阅卷判分"""
    dashscope.api_key = api_key
    user_prompt = f"""
    题目总分：{total_score}分
    标准参考答案：
    {standard_ans}
    学生作答内容：
    {student_text}
    
    批改要求：
    1. 对照参考答案得分要点批改，标注遗漏、错误步骤；
    2. 输出最终得分 + 简短扣分理由。
    """
    messages = [
        {"role": "system", "content": "专业阅卷老师，按要点客观打分，回答简洁"},
        {"role": "user", "content": user_prompt}
    ]
    response = Generation.call(
        model="qwen-turbo",
        messages=messages,
        result_format="message"
    )
    if response.status_code == 200:
        res = response.output.choices[0].message.content
        print("\n===== 阅卷打分结果 =====")
        print(res)
        return res
    else:
        print(f"文本模型调用失败！错误码：{response.code}, 错误信息：{response.message}")
        return None

# 统一入口函数：传入图片路径、参考答案、总分、密钥，一键完成识别+批改
def paper_scoring_main(img_path, standard_answer, total_score, api_key):
    # 1. OCR提取文字
    stu_answer_text = qwen_vlm_ocr_extract(img_path, api_key)
    if not stu_answer_text:
        return None
    # 2. LLM判分
    score_result = qwen_text_judge(stu_answer_text, standard_answer, total_score, api_key)
    return score_result

# 调用示例
if __name__ == "__main__":
    AK = "你的dashscope_api_key"
    img = "student_paper.jpg"
    ref_ans = """参考答案：
1. xxx；
2. xxx；
总分5分，两点各2分，书写规范1分。"""
    paper_scoring_main(img, ref_ans, 5, AK)