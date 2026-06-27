import ssl
import certifi

_original_create_default_context = ssl.create_default_context

def fixed_context(*args, **kwargs):
    return _original_create_default_context(
        cafile=certifi.where()
    )

ssl.create_default_context = fixed_context
from paddleocr import PaddleOCR


class OCRService:

    def __init__(self):

        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang="en"
        )

    # def extract_text(
    #     self,
    #     image_path: str,
    # ):

    #     result = self.ocr.ocr(image_path)

    #     extracted_lines = []

    #     for page in result:

    #         if page is None:
    #             continue

    #         for line in page:

    #             text = line[1][0]

    #             extracted_lines.append(
    #                 text
    #             )

    #     return extracted_lines

    def extract_text(self, image_path: str):

        result = self.ocr.ocr(
            image_path,
            cls=True
        )

        extracted_lines = []

        for page in result:

            if page is None:
                continue

            for line in page:

                text = line[1][0]

                extracted_lines.append(
                {
                    "text": text,
                    "bbox": line[0],
                    "confidence": float(line[1][1])
                }
            )

        return extracted_lines