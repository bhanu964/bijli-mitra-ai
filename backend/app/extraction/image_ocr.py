import io
import fitz
import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import List, Dict, Any

class ImageOCR:
    @staticmethod
    def preprocess_image(pil_img: Image.Image) -> Image.Image:
        """
        Enhances contrast, converts to grayscale, and applies CLAHE + Otsu thresholding.
        """
        img_np = np.array(pil_img)
        if len(img_np.shape) == 3:
            # Check if image has narrow width
            h, w = img_np.shape[:2]
            if w < 1200:
                scale = max(1.0, 1200.0 / w)
                img_np = cv2.resize(img_np, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LANCZOS4)
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_np
            h, w = gray.shape[:2]
            if w < 1200:
                scale = max(1.0, 1200.0 / w)
                gray = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LANCZOS4)

        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return Image.fromarray(thresh)

    @classmethod
    def ocr_pdf(cls, pdf_path: str, dpi: int = 250) -> List[Dict[str, Any]]:
        """
        Renders PDF pages as images and runs Tesseract OCR.
        """
        results = []
        doc = fitz.open(pdf_path)
        for i in range(len(doc)):
            page = doc[i]
            pix = page.get_pixmap(dpi=dpi)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            processed = cls.preprocess_image(img)
            text = pytesseract.image_to_string(processed, config="--psm 6")
            if len(text.strip()) < 50:
                text_fallback = pytesseract.image_to_string(processed, config="--psm 4")
                text = f"{text}\n{text_fallback}"
            results.append({
                "page_number": i + 1,
                "text": text,
                "confidence": 0.90 if len(text.strip()) > 50 else 0.45
            })
        doc.close()
        return results

    @classmethod
    def ocr_image_file(cls, image_path: str) -> Dict[str, Any]:
        """
        Performs high-resolution multi-pass multi-band OCR on JPG/PNG mobile photos and thermal receipts.
        Combines red-channel contrast enhancement, morphological dot-matrix closing,
        and vertical band slicing (USCNO zone, Top, Mid, Bottom, Full).
        """
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            pil_img = Image.open(image_path)
            img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        h, w = img_bgr.shape[:2]
        target_w = 1400
        scale = max(1.0, target_w / w)
        scaled_bgr = cv2.resize(img_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LANCZOS4)

        # Red channel provides maximum contrast for blue/purple thermal ribbon ink
        red_ch = scaled_bgr[:, :, 2]
        norm_r = cv2.normalize(red_ch, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

        # Morphological closing bridges dot-matrix dots into continuous readable characters
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        closed = cv2.morphologyEx(norm_r, cv2.MORPH_CLOSE, kernel)
        _, th_full = cv2.threshold(closed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 1. Full image pass (--psm 6 and --psm 4)
        t_full_6 = pytesseract.image_to_string(th_full, config="--psm 6")
        t_full_4 = pytesseract.image_to_string(th_full, config="--psm 4")

        # 2. USCNO zone crop (24% to 33% where USCNO and SCNO are located)
        uscno_crop = closed[int(closed.shape[0]*0.24):int(closed.shape[0]*0.33), :]
        _, th_uscno = cv2.threshold(uscno_crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        t_uscno = pytesseract.image_to_string(th_uscno, config="--psm 6")

        # 3. Top band (0% to 45% for header, utility, consumer name, category, load)
        top_crop = closed[0:int(closed.shape[0]*0.45), :]
        _, th_top = cv2.threshold(top_crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        t_top = pytesseract.image_to_string(th_top, config="--psm 6")

        # 4. Middle band (30% to 70% for meter readings and billed units)
        mid_crop = closed[int(closed.shape[0]*0.30):int(closed.shape[0]*0.70), :]
        _, th_mid = cv2.threshold(mid_crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        t_mid = pytesseract.image_to_string(th_mid, config="--psm 6")

        # 5. Bottom band (55% to 100% for charges, arrears, net amounts)
        bot_crop = closed[int(closed.shape[0]*0.55):, :]
        _, th_bot = cv2.threshold(bot_crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        t_bot = pytesseract.image_to_string(th_bot, config="--psm 6")

        # 6. Footer band (70% to 100% for net amount, last paid amount, due dates, helpline)
        foot_crop = closed[int(closed.shape[0]*0.70):, :]
        _, th_foot = cv2.threshold(foot_crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        t_foot = pytesseract.image_to_string(th_foot, config="--psm 6")

        # 7. Grayscale CLAHE pass for standard photographic paper bills
        gray = cv2.cvtColor(scaled_bgr, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        cl_gray = clahe.apply(gray)
        t_gray = pytesseract.image_to_string(cl_gray, config="--psm 6")

        combined_text = (
            f"--- USCNO ZONE ---\n{t_uscno}\n"
            f"--- TOP BAND ---\n{t_top}\n"
            f"--- MID BAND ---\n{t_mid}\n"
            f"--- BOT BAND ---\n{t_bot}\n"
            f"--- FOOTER BAND ---\n{t_foot}\n"
            f"--- FULL PSM6 ---\n{t_full_6}\n"
            f"--- FULL PSM4 ---\n{t_full_4}\n"
            f"--- GRAY CLAHE ---\n{t_gray}"
        )

        return {
            "page_number": 1,
            "text": combined_text,
            "confidence": 0.95 if len(combined_text.strip()) > 50 else 0.40
        }
