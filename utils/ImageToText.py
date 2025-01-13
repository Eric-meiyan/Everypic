import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

class ImageToText:
    def __init__(self, model_name="Salesforce/blip-image-captioning-large"):
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(model_name)
    
    def caption_image(self, image_path, conditional_text=None):
        """
        Generate caption for an image
        Args:
            image_path: Path to the image file or URL
            conditional_text: Optional text prompt for conditional captioning
        Returns:
            str: Generated caption
        """
        # Load image
        if image_path.startswith(('http://', 'https://')):
            raw_image = Image.open(requests.get(image_path, stream=True).raw).convert('RGB')
        else:
            raw_image = Image.open(image_path)
        
        if conditional_text:
            # Conditional captioning
            inputs = self.processor(raw_image, conditional_text, return_tensors="pt")
        else:
            # Unconditional captioning
            inputs = self.processor(raw_image, return_tensors="pt")
        
        out = self.model.generate(**inputs)
        return self.processor.decode(out[0], skip_special_tokens=True)

# Example usage:
# captioner = ImageToText()
# caption = captioner.caption_image("path/to/image.jpg")
# caption_with_prompt = captioner.caption_image("path/to/image.jpg", "A photo of:")
