#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p backend/database
mkdir -p backend/static/img

# Create log files
touch backend/database/log_absensi.txt
touch backend/database/log_vote.txt

# Create placeholder images using PIL
python3 << 'EOF'
try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'Pillow'])
    from PIL import Image, ImageDraw

import os

# Create placeholder candidate images
for i in range(1, 4):
    img = Image.new('RGB', (300, 300), color=(212, 217, 74))
    draw = ImageDraw.Draw(img)
    draw.text((100, 140), f'Kandidat {i}', fill=(0, 0, 0))
    img.save(f'backend/static/img/candidate{i}.png')
    print(f"Created candidate{i}.png")

# Create logo placeholder
img = Image.new('RGB', (200, 200), color=(212, 217, 74))
draw = ImageDraw.Draw(img)
draw.text((40, 90), 'HIMATE', fill=(0, 0, 0))
img.save('backend/static/img/himate_logo.png')
print("Created himate_logo.png")

print("All placeholder images created successfully!")
EOF

echo "Setup complete! Run: python backend/app.py"
