import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

class ImageToText:
    def __init__(self, model_name="Salesforce/blip-image-captioning-large"):
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
    
    def caption_image(self, image_path, conditional_text="用中文描述这张图片。请详细描述图片中的内容："):
        """
        Generate caption for an image in Chinese
        Args:
            image_path: Path to the image file or URL
            conditional_text: Chinese text prompt for conditional captioning
        Returns:
            str: Generated caption in Chinese
        """
        # Check if model is loaded
        if self.processor is None or self.model is None:
            raise RuntimeError("Model not loaded. Please call load_model() first.")
        
        # Load image
        if image_path.startswith(('http://', 'https://')):
            raw_image = Image.open(requests.get(image_path, stream=True).raw).convert('RGB')
        else:
            raw_image = Image.open(image_path)
        
        inputs = self.processor(raw_image, conditional_text, return_tensors="pt")
        
        # 优化参数以提高中文生成质量
        out = self.model.generate(
            **inputs,
            max_length=150,          # 增加最大长度，因为中文描述通常需要更多token
            min_length=30,           # 适当增加最小长度
            num_beams=8,             # 增加束搜索数量以获得更好的生成结果
            length_penalty=1.5,      # 增加长度惩罚以鼓励生成更长的描述
            temperature=0.8,         # 略微增加随机性
            repetition_penalty=1.5,  # 增加重复惩罚
            do_sample=True,          # 启用采样以增加多样性
            top_k=50,               # 限制词表大小
            top_p=0.9               # 使用核采样
        )
        
        return self.processor.decode(out[0], skip_special_tokens=True)

# Example usage:
# captioner = ImageToText()
# caption = captioner.caption_image("path/to/image.jpg")
# caption_with_prompt = captioner.caption_image("path/to/image.jpg", "A photo of:")
