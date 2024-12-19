# LivePhoto Best Frame Picker 📸

Turn your iPhone Live Photos into perfect still images automatically! This Python tool analyzes your Live Photo videos (MP4) and extracts the best frame using computer vision techniques, making it perfect for creating photo albums, calendars, or any other project where you need the perfect shot.

## 🌟 The Story Behind

This tool was born from a real need: creating a family photo calendar. When working with iPhone Live Photos exported as MP4s, I needed a way to automatically select the best frame from each video - you know, the one where everyone's eyes are open and the shot is perfectly focused!

Instead of manually scrubbing through each video to find the perfect moment, this tool does it automatically using computer vision to analyze frame sharpness and quality.

## 🎯 Perfect For

- Creating photo calendars (like Hofmann)
- Selecting the best still from Live Photos
- Batch processing multiple Live Photos
- Photo album creation
- Social media content preparation

## ✨ Features

- 🔍 Automatically finds the sharpest frame in each video
- 📁 Processes entire directories of MP4 files
- 🎨 Supports both JPG and PNG output formats
- 📊 Detailed logging for tracking progress
- 💪 Robust error handling
- 🖥️ Simple command-line interface

## 🚀 Quick Start

```bash
# Install requirements
pip install opencv-python

# Run the script
python frame_extractor.py /path/to/your/videos
```

## 💡 Usage Examples

Basic usage (output to default folder):
```bash
python frame_extractor.py /path/to/live/photos
```

Specify output format:
```bash
python frame_extractor.py /path/to/live/photos -f png
```

Custom output directory:
```bash
python frame_extractor.py /path/to/live/photos -o /path/to/output
```

## 🛠️ How It Works

The tool uses computer vision techniques to:
1. Read each frame of the video
2. Calculate frame sharpness using Laplacian variance
3. Track and save the frame with the highest quality score
4. Output the best frame as an image file

## 🤝 Contributing

Feel free to open issues or submit pull requests if you have ideas for improvements!

## 📝 License

MIT License - feel free to use this in your own projects!

## 🙏 Acknowledgments

This project was developed with the assistance of AI tools and the open-source community, demonstrating how modern technology can solve everyday problems in creative ways.

---

Made with ❤️ and AI assistance | [Follow me on GitHub](https://github.com/adpablos)