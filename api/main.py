from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import qrcode
import boto3
import os
from io import BytesIO
import re

# Loading Environment variable (AWS Access Key and Secret Key)
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Allowing CORS for local testing
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS S3 Configuration
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
)

bucket_name = 'shoma-qr-code-bucket'

@app.post("/generate-qr/")
async def generate_qr(url: str):
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR Code to BytesIO object
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    
    # Convert to bytes for S3
    img_bytes = img_byte_arr.getvalue()

    # Sanitize file name for S3
    url_part = url.split('//')[-1]
    sanitized_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', url_part)
    file_name = f"qr_codes/{sanitized_name}.png"

    try:
        # Upload to S3
        s3.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=img_bytes,
        ContentType='image/png'
        # remove ACL, bucket enforces ownership
        )
        
        # Generate the S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        return {"qr_code_url": s3_url}

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # <-- prints full error to console for debugging
        raise HTTPException(status_code=500, detail=str(e))
