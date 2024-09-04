import transformers
import torch

SYSTEM_PROMPT_SUMMARIZATION = """Please analyze and summarize the arXiv paper into a **Korean** AI newsletter. Include technical keywords in English where necessary, especially if they are not commonly used in Korean. You don't need to provide an English summary, but please label each section (e.g., Introduction, Related Works) in English if it is present.
"""

class LlamaTextGenerator:
    def __init__(self, model_id: str, max_length: int = 25600):
        """
        LlamaTextGenerator 초기화
        :param model_id: Llama3.1 모델 경로
        :param max_length: 생성할 텍스트의 최대 길이
        """
        self.model_id = model_id
        self.max_length = max_length
        self.pipeline = self._initialize_pipeline()

    def _initialize_pipeline(self):
        """
        Llama3.1 모델 파이프라인 초기화
        :return: 텍스트 생성 파이프라인
        """
        return transformers.pipeline(
            "text-generation",
            model=self.model_id,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto",
        )

    def generate_summary(self, text_input: str, temperature: float = 0.7) -> str:
        """
        입력된 텍스트를 요약하여 반환
        :param text_input: 요약할 텍스트 입력
        :return: 모델이 생성한 요약 텍스트
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_SUMMARIZATION},
            {"role": "user", "content": text_input},
        ]
        
        outputs = self.pipeline(
            messages,
            max_new_tokens=self.max_length,
            temperature=temperature
        )
        
        return outputs[0]["generated_text"][-1]['content']

# 사용 예시
if __name__ == "__main__":
    model_id = "/root/Desktop/workspace/Yunseok/sub_projects/paper_summary/Meta-Llama-3.1-8B-Instruct"
    
    # 클래스 인스턴스 생성
    text_generator = LlamaTextGenerator(model_id)
    
    # 텍스트 입력
    text_input = "Please summarize the main findings of the following research paper."
    
    # 요약 생성
    summary = text_generator.generate_summary(text_input)
    
    print(summary)
