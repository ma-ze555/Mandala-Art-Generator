# AI Mandala Art Generator

Generate beautiful mandala art using AI, powered by Hugging Face's FLUX.1 model.

## Features

- Generate unique mandala art from text prompts
- Multiple style options (Monochrome, Colorful, Geometric, Floral)
- Download and share generated images

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/mandala-art-generator.git
cd mandala-art-generator
```

**2. Add your Hugging Face token**
```bash
cp .env.example .env
```
Open `.env` and replace `your_huggingface_token_here` with your actual token.
Get a free token at: https://huggingface.co/settings/tokens

**3. Run the server**
```bash
python server.py
```

**4. Open in browser**
```
http://localhost:8080
```

## Requirements

- Python 3.x
- A free Hugging Face account and API token

## Developed by Code Club
🌍 Live Website: 
<br>
https://mandala-art-generator-hazel.vercel.app/
