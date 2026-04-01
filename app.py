# # from flask import Flask, request, render_template, send_file
# # from PIL import Image, ImageOps
# # from io import BytesIO
# # from dotenv import load_dotenv
# # import requests
# # import cloudinary
# # import cloudinary.uploader
# # import cloudinary.utils
# # import os

# # app = Flask(__name__)

# # REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")

# # cloudinary.config(
# #     cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
# #     api_key=os.getenv("CLOUDINARY_API_KEY"),
# #     api_secret=os.getenv("CLOUDINARY_API_SECRET"),
# # )


# # @app.route("/")
# # def index():
# #     return render_template("index.html")


# # def process_single_image(input_image_bytes):
# #     """Remove background, enhance, and return a ready-to-paste passport PIL image."""
# #     # Step 1: Background removal
# #     response = requests.post(
# #         "https://api.remove.bg/v1.0/removebg",
# #         files={"image_file": input_image_bytes},
# #         data={"size": "auto"},
# #         headers={"X-Api-Key": REMOVE_BG_API_KEY},
# #     )

# #     if response.status_code != 200:
# #         try:
# #             error_info = response.json()
# #             if error_info.get("errors"):
# #                 error_code = error_info["errors"][0].get("code", "unknown_error")
# #                 raise ValueError(f"bg_removal_failed:{error_code}:{response.status_code}")
# #         except ValueError:
# #             raise
# #         except Exception:
# #             pass
# #         raise ValueError(f"bg_removal_failed:unknown:{response.status_code}")

# #     bg_removed = BytesIO(response.content)
# #     img = Image.open(bg_removed)

# #     if img.mode in ("RGBA", "LA"):
# #         background = Image.new("RGB", img.size, (255, 255, 255))
# #         background.paste(img, mask=img.split()[-1])
# #         processed_img = background
# #     else:
# #         processed_img = img.convert("RGB")

# #     # Step 2: Upload to Cloudinary
# #     buffer = BytesIO()
# #     processed_img.save(buffer, format="PNG")
# #     buffer.seek(0)
# #     upload_result = cloudinary.uploader.upload(buffer, resource_type="image")
# #     image_url = upload_result.get("secure_url")
# #     public_id = upload_result.get("public_id")

# #     if not image_url:
# #         raise ValueError("cloudinary_upload_failed")

# #     # Step 3: Enhance via Cloudinary AI
# #     enhanced_url = cloudinary.utils.cloudinary_url(
# #         public_id,
# #         transformation=[
# #             {"effect": "gen_restore"},
# #             {"quality": "auto"},
# #             {"fetch_format": "auto"},
# #         ],
# #     )[0]

# #     enhanced_img_data = requests.get(enhanced_url).content
# #     img = Image.open(BytesIO(enhanced_img_data))

# #     if img.mode in ("RGBA", "LA"):
# #         background = Image.new("RGB", img.size, (255, 255, 255))
# #         background.paste(img, mask=img.split()[-1])
# #         passport_img = background
# #     else:
# #         passport_img = img.convert("RGB")

# #     return passport_img


# # @app.route("/process", methods=["POST"])
# # def process():
# #     print("==== /process endpoint hit ====")

# #     # Layout settings
# #     passport_width = int(request.form.get("width", 390))
# #     passport_height = int(request.form.get("height", 480))
# #     border = int(request.form.get("border", 2))
# #     spacing = int(request.form.get("spacing", 10))
# #     margin_x = 10
# #     margin_y = 10
# #     horizontal_gap = 10
# #     a4_w, a4_h = 2480, 3508

# #     # Collect images and their copy counts
# #     # Supports: image_0, image_1, ... and copies_0, copies_1, ...
# #     # Also supports legacy single: image + copies
# #     images_data = []

# #     # Multi-image mode
# #     i = 0
# #     while f"image_{i}" in request.files:
# #         file = request.files[f"image_{i}"]
# #         copies = int(request.form.get(f"copies_{i}", 6))
# #         images_data.append((file.read(), copies))
# #         i += 1

# #     # Fallback to single image mode
# #     if not images_data and "image" in request.files:
# #         file = request.files["image"]
# #         copies = int(request.form.get("copies", 6))
# #         images_data.append((file.read(), copies))

# #     if not images_data:
# #         return "No image uploaded", 400

# #     print(f"DEBUG: Processing {len(images_data)} image(s)")

# #     # Process all images
# #     passport_images = []
# #     for idx, (img_bytes, copies) in enumerate(images_data):
# #         print(f"DEBUG: Processing image {idx + 1} with {copies} copies")
# #         try:
# #             img = process_single_image(img_bytes)
# #             img = img.resize((passport_width, passport_height), Image.LANCZOS)
# #             img = ImageOps.expand(img, border=border, fill="black")
# #             passport_images.append((img, copies))
# #         except ValueError as e:
# #             err_str = str(e)
# #             if "410" in err_str or "face" in err_str.lower():
# #                 return {"error": "face_detection_failed"}, 410
# #             elif "429" in err_str or "quota" in err_str.lower():
# #                 return {"error": "quota_exceeded"}, 429
# #             else:
# #                 print(err_str)
# #                 return {"error": err_str}, 500
                

# #     paste_w = passport_width + 2 * border
# #     paste_h = passport_height + 2 * border

# #     # Build all pages
# #     pages = []
# #     current_page = Image.new("RGB", (a4_w, a4_h), "white")
# #     x, y = margin_x, margin_y

# #     def new_page():
# #         nonlocal current_page, x, y
# #         pages.append(current_page)
# #         current_page = Image.new("RGB", (a4_w, a4_h), "white")
# #         x, y = margin_x, margin_y

# #     for passport_img, copies in passport_images:
# #         for _ in range(copies):
# #             # Move to next row if needed
# #             if x + paste_w > a4_w - margin_x:
# #                 x = margin_x
# #                 y += paste_h + spacing

# #             # Move to next page if needed
# #             if y + paste_h > a4_h - margin_y:
# #                 new_page()

# #             current_page.paste(passport_img, (x, y))
# #             print(f"DEBUG: Placed at x={x}, y={y}")
# #             x += paste_w + horizontal_gap

# #     pages.append(current_page)
# #     print(f"DEBUG: Total pages = {len(pages)}")

# #     # Export multi-page PDF
# #     output = BytesIO()
# #     if len(pages) == 1:
# #         pages[0].save(output, format="PDF", dpi=(300, 300))
# #     else:
# #         pages[0].save(
# #             output,
# #             format="PDF",
# #             dpi=(300, 300),
# #             save_all=True,
# #             append_images=pages[1:],
# #         )
# #     output.seek(0)
# #     print("DEBUG: Returning PDF to client")

# #     return send_file(
# #         output,
# #         mimetype="application/pdf",
# #         as_attachment=True,
# #         download_name="passport-sheet.pdf",
# #     )


# # if __name__ == "__main__":
# #     app.run(host="0.0.0.0", port=5000, debug=True)


# from flask import Flask, request, render_template, send_file
# from PIL import Image, ImageOps, ImageDraw, ImageFont
# from io import BytesIO
# from dotenv import load_dotenv
# import requests
# import cloudinary
# import cloudinary.uploader
# import cloudinary.utils
# import os

# app = Flask(__name__)

# REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")

# cloudinary.config(
#     cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
#     api_key=os.getenv("CLOUDINARY_API_KEY"),
#     api_secret=os.getenv("CLOUDINARY_API_SECRET"),
# )

# @app.route("/")
# def index():
#     return render_template("index.html")

# def hex_to_rgb(hex_color):
#     """Convert #RRGGBB hex string to RGB tuple"""
#     hex_color = hex_color.lstrip('#')
#     return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# def process_single_image(input_image_bytes, remove_bg=False, bg_color_hex="#ffffff"):
#     """Remove background (if enabled), composite color, enhance, and return PIL image."""
#     bg_color_rgb = hex_to_rgb(bg_color_hex)
    
#     # Step 1: Background handling
#     if remove_bg:
#         response = requests.post(
#             "https://api.remove.bg/v1.0/removebg",
#             files={"image_file": input_image_bytes},
#             data={"size": "auto"},
#             headers={"X-Api-Key": REMOVE_BG_API_KEY},
#         )

#         if response.status_code != 200:
#             try:
#                 error_info = response.json()
#                 if error_info.get("errors"):
#                     error_code = error_info["errors"][0].get("code", "unknown_error")
#                     raise ValueError(f"bg_removal_failed:{error_code}:{response.status_code}")
#             except ValueError:
#                 raise
#             except Exception:
#                 pass
#             raise ValueError(f"bg_removal_failed:unknown:{response.status_code}")

#         bg_removed = BytesIO(response.content)
#         img = Image.open(bg_removed)
#     else:
#         # User didn't want BG removed, just read the original image
#         img = Image.open(BytesIO(input_image_bytes))

#     # Apply Background color (if image has transparency or background was removed)
#     if img.mode in ("RGBA", "LA"):
#         background = Image.new("RGB", img.size, bg_color_rgb)
#         background.paste(img, mask=img.split()[-1])
#         processed_img = background
#     else:
#         processed_img = img.convert("RGB")

#     # Step 2: Upload to Cloudinary for enhancement
#     buffer = BytesIO()
#     processed_img.save(buffer, format="PNG")
#     buffer.seek(0)
#     upload_result = cloudinary.uploader.upload(buffer, resource_type="image")
#     image_url = upload_result.get("secure_url")
#     public_id = upload_result.get("public_id")

#     if not image_url:
#         raise ValueError("cloudinary_upload_failed")

#     # Step 3: Enhance via Cloudinary AI
#     enhanced_url = cloudinary.utils.cloudinary_url(
#         public_id,
#         transformation=[
#             {"effect": "gen_restore"},
#             {"quality": "auto"},
#             {"fetch_format": "auto"},
#         ],
#     )[0]

#     enhanced_img_data = requests.get(enhanced_url).content
#     final_img = Image.open(BytesIO(enhanced_img_data)).convert("RGB")

#     return final_img


# @app.route("/process", methods=["POST"])
# def process():
#     print("==== /process endpoint hit ====")

#     # Layout settings
#     passport_width = int(request.form.get("width", 390))
#     passport_height = int(request.form.get("height", 480))
#     border = int(request.form.get("border", 2))
#     spacing = int(request.form.get("spacing", 10))
    
#     # NEW Advanced Options
#     remove_bg_str = request.form.get("removeBg", "false").lower() == "true"
#     bg_color_hex = request.form.get("bgColor", "#ffffff")
#     add_text_str = request.form.get("addText", "false").lower() == "true"
#     photo_name = request.form.get("photoName", "").strip()
#     photo_date = request.form.get("photoDate", "").strip()

#     margin_x = 10
#     margin_y = 10
#     horizontal_gap = 10
#     a4_w, a4_h = 2480, 3508

#     # Collect images and their copy counts
#     images_data = []

#     # Multi-image mode
#     i = 0
#     while f"image_{i}" in request.files:
#         file = request.files[f"image_{i}"]
#         copies = int(request.form.get(f"copies_{i}", 6))
#         images_data.append((file.read(), copies))
#         i += 1

#     # Fallback to single image mode
#     if not images_data and "image" in request.files:
#         file = request.files["image"]
#         copies = int(request.form.get("copies", 6))
#         images_data.append((file.read(), copies))

#     if not images_data:
#         return "No image uploaded", 400

#     print(f"DEBUG: Processing {len(images_data)} image(s). Remove BG: {remove_bg_str}, Add Text: {add_text_str}")

#     # Process all images
#     passport_images = []
#     for idx, (img_bytes, copies) in enumerate(images_data):
#         print(f"DEBUG: Processing image {idx + 1} with {copies} copies")
#         try:
#             # Pass our new variables to the processor
#             img = process_single_image(img_bytes, remove_bg=remove_bg_str, bg_color_hex=bg_color_hex)
#             img = img.resize((passport_width, passport_height), Image.LANCZOS)
            
#             # --- NEW: DRAW TEXT STRIP (NAME & DATE) ---
#             if add_text_str and (photo_name or photo_date):
#                 draw = ImageDraw.Draw(img)
                
#                 # Load a standard font or use default (adjust size if needed)
#                 try:
#                     font = ImageFont.truetype("arial.ttf", 26) # Windows system font
#                 except IOError:
#                     try:
#                         font = ImageFont.truetype("DejaVuSans.ttf", 26) # Linux system font
#                     except IOError:
#                         font = ImageFont.load_default() # Fallback if no fonts found
                
#                 # Setup rectangle for text
#                 rect_height = int(passport_height * 0.18) # 18% of the image height for text area
#                 rect_y = passport_height - rect_height
                
#                 # Draw white box
#                 draw.rectangle([(0, rect_y), (passport_width, passport_height)], fill="white")
                
#                 # Prepare Multiline Text
#                 lines = []
#                 if photo_name: lines.append(photo_name)
#                 if photo_date: lines.append(photo_date)
#                 text = "\n".join(lines)
                
#                 # Calculate text position to center it
#                 bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
#                 text_w = bbox[2] - bbox[0]
#                 text_h = bbox[3] - bbox[1]
                
#                 text_x = (passport_width - text_w) / 2
#                 text_y = rect_y + (rect_height - text_h) / 2
                
#                 # Draw Text
#                 draw.multiline_text((text_x, text_y), text, fill="black", font=font, align="center")
#             # ------------------------------------------

#             # Apply Border after everything
#             img = ImageOps.expand(img, border=border, fill="black")
#             passport_images.append((img, copies))
            
#         except ValueError as e:
#             err_str = str(e)
#             if "410" in err_str or "face" in err_str.lower():
#                 return {"error": "face_detection_failed"}, 410
#             elif "429" in err_str or "quota" in err_str.lower():
#                 return {"error": "quota_exceeded"}, 429
#             else:
#                 print(err_str)
#                 return {"error": err_str}, 500
                

#     paste_w = passport_width + 2 * border
#     paste_h = passport_height + 2 * border

#     # Build all pages
#     pages = []
#     current_page = Image.new("RGB", (a4_w, a4_h), "white")
#     x, y = margin_x, margin_y

#     def new_page():
#         nonlocal current_page, x, y
#         pages.append(current_page)
#         current_page = Image.new("RGB", (a4_w, a4_h), "white")
#         x, y = margin_x, margin_y

#     for passport_img, copies in passport_images:
#         for _ in range(copies):
#             # Move to next row if needed
#             if x + paste_w > a4_w - margin_x:
#                 x = margin_x
#                 y += paste_h + spacing

#             # Move to next page if needed
#             if y + paste_h > a4_h - margin_y:
#                 new_page()

#             current_page.paste(passport_img, (x, y))
#             print(f"DEBUG: Placed at x={x}, y={y}")
#             x += paste_w + horizontal_gap

#     pages.append(current_page)
#     print(f"DEBUG: Total pages = {len(pages)}")

#     # Export multi-page PDF
#     output = BytesIO()
#     if len(pages) == 1:
#         pages[0].save(output, format="PDF", dpi=(300, 300))
#     else:
#         pages[0].save(
#             output,
#             format="PDF",
#             dpi=(300, 300),
#             save_all=True,
#             append_images=pages[1:],
#         )
#     output.seek(0)
#     print("DEBUG: Returning PDF to client")

#     return send_file(
#         output,
#         mimetype="application/pdf",
#         as_attachment=True,
#         download_name="passport-sheet.pdf",
#     )


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, request, render_template, send_file
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO
from dotenv import load_dotenv
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.utils
import os

app = Flask(__name__)

# Load environment variables (Make sure your .env file is present)
load_dotenv()

REMOVE_BG_API_KEY = os.getenv("REMOVE_BG_API_KEY")

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

@app.route("/")
def index():
    return render_template("index.html")

def hex_to_rgb(hex_color):
    """Convert #RRGGBB hex string to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def process_single_image(input_image_bytes, remove_bg=False, bg_color_hex="#ffffff", bg_image_bytes=None):
    """Remove background (if enabled), composite custom color or image, enhance, and return PIL image."""
    
    # Step 1: Background handling
    if remove_bg:
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": input_image_bytes},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVE_BG_API_KEY},
        )

        if response.status_code != 200:
            try:
                error_info = response.json()
                if error_info.get("errors"):
                    error_code = error_info["errors"][0].get("code", "unknown_error")
                    raise ValueError(f"bg_removal_failed:{error_code}:{response.status_code}")
            except ValueError:
                raise
            except Exception:
                pass
            raise ValueError(f"bg_removal_failed:unknown:{response.status_code}")

        bg_removed = BytesIO(response.content)
        img = Image.open(bg_removed)
    else:
        # User didn't want BG removed, just read the original image
        img = Image.open(BytesIO(input_image_bytes))

    # Apply Background color OR Background Image (if image has transparency or background was removed)
    if img.mode in ("RGBA", "LA"):
        if bg_image_bytes:
            # Custom Image Background
            bg_layer = Image.open(BytesIO(bg_image_bytes)).convert("RGB")
            # Resize and crop the background image to match the passport photo dimensions
            bg_layer = ImageOps.fit(bg_layer, img.size, Image.LANCZOS)
            bg_layer.paste(img, mask=img.split()[-1])
            processed_img = bg_layer
        else:
            # Solid Color Background
            bg_color_rgb = hex_to_rgb(bg_color_hex)
            background = Image.new("RGB", img.size, bg_color_rgb)
            background.paste(img, mask=img.split()[-1])
            processed_img = background
    else:
        processed_img = img.convert("RGB")

    # Step 2: Upload to Cloudinary for enhancement
    buffer = BytesIO()
    processed_img.save(buffer, format="PNG")
    buffer.seek(0)
    upload_result = cloudinary.uploader.upload(buffer, resource_type="image")
    image_url = upload_result.get("secure_url")
    public_id = upload_result.get("public_id")

    if not image_url:
        raise ValueError("cloudinary_upload_failed")

    # Step 3: Enhance via Cloudinary AI (gen_restore for face enhancement)
    enhanced_url = cloudinary.utils.cloudinary_url(
        public_id,
        transformation=[
            {"effect": "gen_restore"},
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )[0]

    enhanced_img_data = requests.get(enhanced_url).content
    final_img = Image.open(BytesIO(enhanced_img_data)).convert("RGB")

    return final_img


@app.route("/process", methods=["POST"])
def process():
    print("==== /process endpoint hit ====")

    # Layout settings
    passport_width = int(request.form.get("width", 390))
    passport_height = int(request.form.get("height", 480))
    border = int(request.form.get("border", 2))
    spacing = int(request.form.get("spacing", 10))
    
    # Extract Background Options
    remove_bg_str = request.form.get("removeBg", "false").lower() == "true"
    bg_type = request.form.get("bgType", "color")
    bg_color_hex = request.form.get("bgColor", "#ffffff")
    
    bg_image_file = request.files.get("bgImage")
    bg_image_bytes = bg_image_file.read() if bg_image_file else None

    # Extract Text Options
    add_text_str = request.form.get("addText", "false").lower() == "true"
    photo_name = request.form.get("photoName", "").strip()
    photo_date = request.form.get("photoDate", "").strip()

    margin_x = 10
    margin_y = 10
    horizontal_gap = 10
    a4_w, a4_h = 2480, 3508

    # Collect images and their copy counts
    images_data = []

    # Multi-image mode
    i = 0
    while f"image_{i}" in request.files:
        file = request.files[f"image_{i}"]
        copies = int(request.form.get(f"copies_{i}", 6))
        images_data.append((file.read(), copies))
        i += 1

    # Fallback to single image mode
    if not images_data and "image" in request.files:
        file = request.files["image"]
        copies = int(request.form.get("copies", 6))
        images_data.append((file.read(), copies))

    if not images_data:
        return {"error": "No image uploaded"}, 400

    print(f"DEBUG: Processing {len(images_data)} image(s). Remove BG: {remove_bg_str}, Add Text: {add_text_str}")

    # Process all images
    passport_images = []
    for idx, (img_bytes, copies) in enumerate(images_data):
        print(f"DEBUG: Processing image {idx + 1} with {copies} copies")
        try:
            # Pass background options to the processor
            img = process_single_image(
                img_bytes, 
                remove_bg=remove_bg_str, 
                bg_color_hex=bg_color_hex if bg_type == "color" else "#ffffff",
                bg_image_bytes=bg_image_bytes if bg_type == "image" else None
            )
            
            # Resize to passport dimensions
            img = img.resize((passport_width, passport_height), Image.LANCZOS)
            
            # --- DRAW TEXT STRIP (NAME & DATE) ---
            if add_text_str and (photo_name or photo_date):
                draw = ImageDraw.Draw(img)
                
                # Try loading standard fonts, fallback to default
                try:
                    font = ImageFont.truetype("arial.ttf", 26) # Windows
                except IOError:
                    try:
                        font = ImageFont.truetype("DejaVuSans.ttf", 26) # Linux (e.g., Ubuntu/Docker)
                    except IOError:
                        font = ImageFont.load_default() # Fallback
                
                # Setup white plate (18% of image height)
                rect_height = int(passport_height * 0.18) 
                rect_y = passport_height - rect_height
                
                # Draw white box at the bottom
                draw.rectangle([(0, rect_y), (passport_width, passport_height)], fill="white")
                
                # Prepare Multiline Text
                lines = []
                if photo_name: lines.append(photo_name)
                if photo_date: lines.append(photo_date)
                text = "\n".join(lines)
                
                # Calculate text position to center it perfectly
                bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                
                text_x = (passport_width - text_w) / 2
                text_y = rect_y + (rect_height - text_h) / 2
                
                # Draw Text in Black
                draw.multiline_text((text_x, text_y), text, fill="black", font=font, align="center")
            # -------------------------------------

            # Apply Border after everything
            img = ImageOps.expand(img, border=border, fill="black")
            passport_images.append((img, copies))
            
        except ValueError as e:
            err_str = str(e)
            if "410" in err_str or "face" in err_str.lower():
                return {"error": "face_detection_failed"}, 410
            elif "429" in err_str or "quota" in err_str.lower():
                return {"error": "quota_exceeded"}, 429
            else:
                print(f"Error processing image {idx + 1}: {err_str}")
                return {"error": err_str}, 500
                

    paste_w = passport_width + 2 * border
    paste_h = passport_height + 2 * border

    # Build all pages
    pages = []
    current_page = Image.new("RGB", (a4_w, a4_h), "white")
    x, y = margin_x, margin_y

    def new_page():
        nonlocal current_page, x, y
        pages.append(current_page)
        current_page = Image.new("RGB", (a4_w, a4_h), "white")
        x, y = margin_x, margin_y

    for passport_img, copies in passport_images:
        for _ in range(copies):
            # Move to next row if needed
            if x + paste_w > a4_w - margin_x:
                x = margin_x
                y += paste_h + spacing

            # Move to next page if needed
            if y + paste_h > a4_h - margin_y:
                new_page()

            current_page.paste(passport_img, (x, y))
            x += paste_w + horizontal_gap

    pages.append(current_page)
    print(f"DEBUG: Total pages = {len(pages)}")

    # Export multi-page PDF
    output = BytesIO()
    if len(pages) == 1:
        pages[0].save(output, format="PDF", dpi=(300, 300))
    else:
        pages[0].save(
            output,
            format="PDF",
            dpi=(300, 300),
            save_all=True,
            append_images=pages[1:],
        )
    output.seek(0)
    print("DEBUG: Returning PDF to client")

    return send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="passport-sheet.pdf",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)