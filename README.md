# Instagram Reels Auto-Poster

Automatically post reels to Instagram on a schedule using Python.

## Requirements

- Python 3.7+
- FFmpeg installed on your system
- Instagram account credentials

## Installation

1. Clone this repository:
```bash
git clone https://github.com/HOTHEAD01TH/instagent.git
cd instagent
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. **Important**: Install the specific version of moviepy:
```bash
pip install moviepy==1.0.3
```

4. Create a `.env` file in the project root with your Instagram credentials:
```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

5. Create a `reels` folder in the project root:
```bash
mkdir reels
```

## Usage

1. Place your video files in the `reels` folder

2. Run the script:
```bash
python script.py
```

The bot will:
- Post one reel immediately
- Schedule posts at 13:00, 15:00, 18:00, and 21:00 daily
- Delete videos after successful upload

## Features

- Session caching for faster login
- Automatic video processing
- Scheduled posting
- Error handling and retries
- Automatic file cleanup

## System Requirements

### Windows
```bash
winget install ffmpeg
```

### Mac
```bash
brew install ffmpeg
```

### Linux
```bash
sudo apt install ffmpeg
```

## Troubleshooting

If you encounter any issues:
1. Delete `session.pkl` file if present
2. Ensure correct moviepy version (1.0.3)
3. Check your Instagram credentials
4. Verify FFmpeg installation

## License

MIT License

## Disclaimer

Use this bot responsibly and in accordance with Instagram's terms of service.

