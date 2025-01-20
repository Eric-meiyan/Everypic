import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
# Salesforce/blip-image-captioning-base
# Salesforce/blip-image-captioning-large

class ImageToText:
    def __init__(self, model_name="Salesforce/blip-image-captioning-base"):
        self.model_name = model_name
        self.processor = None
        self.model = None
    
    def load_model(self):
        """
        Load the BLIP model and processor
        """
        if self.processor is None or self.model is None:
            self.processor = BlipProcessor.from_pretrained(self.model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)
    
    def caption_image(self, image_path, conditional_text=None):
        """生成图片描述
        
        Args:
            image_path: 图片文件路径
            conditional_text: 条件文本（可选）
            
        Returns:
            str: 生成的图片描述
        """
        if self.processor is None or self.model is None:
            raise RuntimeError("Model not loaded. Please call load_model() first.")
        
        raw_image = Image.open(image_path).convert('RGB')
        inputs = self.processor(raw_image, conditional_text, return_tensors="pt")
        
        # 调整参数以适应 base 模型
        out = self.model.generate(
            **inputs,
            max_length=100,          # 减小最大长度，base模型不需要太长
            num_beams=5,             # 减小束搜索数量，提高速度
            length_penalty=1.0,      # 调整长度惩罚
            temperature=0.7,         # 调整温度
            repetition_penalty=1.2,  # 调整重复惩罚
            do_sample=True,          # 保持采样以增加多样性
            top_k=50,               # 保持词表限制
            top_p=0.9               # 保持核采样参数
        )
        
        return self.processor.decode(out[0], skip_special_tokens=True)

# Example usage:
# captioner = ImageToText()
# caption = captioner.caption_image("path/to/image.jpg")
# caption_with_prompt = captioner.caption_image("path/to/image.jpg", "A photo of:")
