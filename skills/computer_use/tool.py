import base64
import os
from typing import Optional

def run(action: str, x: Optional[int] = None, y: Optional[int] = None, text: Optional[str] = None, **kwargs) -> str:
    try:
        import pyautogui
    except ImportError:
        return "Error: pyautogui is not installed. Please run `pip install pyautogui mss pillow`."
    
    try:
        if action == "screenshot":
            try:
                import mss
                from PIL import Image
                import io
            except ImportError:
                return "Error: mss or pillow is not installed. Please run `pip install mss pillow`."
            
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # primary monitor
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # Resize if too large
                img.thumbnail((1920, 1080))
                
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=75)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                
                return f"[Screenshot base64 included, length: {len(b64)}]"  # For the actual agent, we'd return a proper image block, but since this is a simple text tool for now, returning the raw base64 might break the text context limit. We'll return it formatted if needed or just save it. Wait, Claude desktop computer use returns base64.
                # Actually, returning huge base64 in a text tool can crash the LLM context if not handled.
                # Let's write the screenshot to workspace and return the file path or just a markdown image link.
                
                img_path = os.path.abspath("screenshot.jpg")
                img.save(img_path)
                return f"Screenshot saved to {img_path}. You can view it by reading the file or using Markdown: ![Screenshot](file:///{img_path.replace(chr(92), '/')})"
                
        elif action == "mouse_move":
            if x is None or y is None:
                return "Error: x and y are required for mouse_move."
            pyautogui.moveTo(x, y)
            return f"Mouse moved to {x}, {y}."
            
        elif action == "mouse_click":
            if x is not None and y is not None:
                pyautogui.click(x, y)
                return f"Clicked at {x}, {y}."
            else:
                pyautogui.click()
                return "Clicked at current position."
                
        elif action == "keyboard_type":
            if not text:
                return "Error: text is required for keyboard_type."
            pyautogui.write(text, interval=0.01)
            return f"Typed: '{text}'"
            
        else:
            return f"Error: Unknown action '{action}'."
            
    except Exception as e:
        return f"Error executing computer_use action '{action}': {str(e)}"
