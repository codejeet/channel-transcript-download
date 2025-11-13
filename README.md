# YouTube Channel Transcript Downloader

A Python script to massively download video transcripts from YouTube channels. This tool fetches all videos from a given YouTube channel and downloads their transcripts in various formats (JSON, TXT, or SRT).

## Features

- Download transcripts from all videos in a YouTube channel
- Support for multiple output formats (JSON, TXT, SRT)
- Multi-language support with fallback options
- Automatic handling of generated and manual transcripts
- Progress logging and error handling
- No API key required (uses scrapetube for video discovery)
- Detailed logging to both console and file

## Requirements

- Python 3.7 or higher
- pip (Python package manager)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd channel-transcript-download
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Download all transcripts from a channel (default: JSON format, English language):

```bash
python youtube_transcript_downloader.py "https://www.youtube.com/@channelname"
```

### Advanced Options

```bash
# Specify output directory
python youtube_transcript_downloader.py "https://www.youtube.com/@channelname" --output my_transcripts

# Choose output format (json, txt, or srt)
python youtube_transcript_downloader.py "https://www.youtube.com/@channelname" --format txt

# Specify preferred languages (tries in order)
python youtube_transcript_downloader.py "https://www.youtube.com/@channelname" --languages en es fr

# Limit number of videos to process
python youtube_transcript_downloader.py "https://www.youtube.com/@channelname" --limit 10

# Enable verbose logging
python youtube_transcript_downloader.py "https://www.youtube.com/@channelname" --verbose
```

### Supported Channel URL Formats

The script supports various YouTube channel URL formats:

- `https://www.youtube.com/@username`
- `https://www.youtube.com/channel/UC...`
- `https://www.youtube.com/c/CustomName`
- `https://www.youtube.com/user/Username`

## Output Formats

### JSON Format
Contains complete transcript data including timing information and metadata:
```json
{
  "video_id": "...",
  "title": "...",
  "language": "English",
  "language_code": "en",
  "is_generated": false,
  "transcript": [
    {
      "text": "...",
      "start": 0.0,
      "duration": 2.5
    }
  ]
}
```

### TXT Format
Plain text format with video metadata and transcript text:
```
Title: Video Title
Video ID: abc123
Language: English (en)
URL: https://www.youtube.com/watch?v=abc123
================================================================================

Transcript text here...
```

### SRT Format
Standard subtitle format compatible with video players:
```
1
00:00:00,000 --> 00:00:02,500
Transcript text here...

2
00:00:02,500 --> 00:00:05,000
More text...
```

## Command-Line Options

```
usage: youtube_transcript_downloader.py [-h] [-o OUTPUT] [-f {json,txt,srt}]
                                        [-l LANGUAGES [LANGUAGES ...]]
                                        [--limit LIMIT] [-v]
                                        channel_url

positional arguments:
  channel_url           YouTube channel URL

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory for transcripts (default: transcripts)
  -f {json,txt,srt}, --format {json,txt,srt}
                        Output format (default: json)
  -l LANGUAGES [LANGUAGES ...], --languages LANGUAGES [LANGUAGES ...]
                        Preferred language codes (default: en)
  --limit LIMIT         Maximum number of videos to process
  -v, --verbose         Enable verbose logging
```

## How It Works

1. **Channel Discovery**: Uses `scrapetube` to fetch all video IDs from the channel without requiring API keys
2. **Transcript Retrieval**: Uses `youtube-transcript-api` to download transcripts for each video
3. **Language Handling**: Attempts to get transcripts in preferred languages, falls back to any available transcript
4. **Error Handling**: Gracefully handles videos without transcripts, disabled transcripts, and unavailable videos
5. **Output**: Saves transcripts in the specified format with sanitized filenames

## Logging

The script creates a `download.log` file in the output directory with detailed information about:
- Videos processed
- Successfully downloaded transcripts
- Failed downloads and reasons
- Overall statistics

## Error Handling

The script handles various error cases:
- Videos with disabled transcripts
- Videos without available transcripts
- Unavailable or private videos
- Rate limiting (Too Many Requests)
- Network errors

## Limitations

- Some videos may not have transcripts available
- Auto-generated transcripts may have lower accuracy
- YouTube may rate-limit requests if too many are made quickly
- Private or age-restricted videos cannot be accessed

## Exit Codes

- `0`: All transcripts downloaded successfully
- `1`: No transcripts were downloaded
- `2`: Some transcripts downloaded, but some failed
- `130`: Interrupted by user (Ctrl+C)

## Examples

### Example 1: Download all transcripts as JSON
```bash
python youtube_transcript_downloader.py "https://www.youtube.com/@veritasium"
```

### Example 2: Download first 5 videos as plain text
```bash
python youtube_transcript_downloader.py "https://www.youtube.com/@3blue1brown" --format txt --limit 5
```

### Example 3: Download with Spanish preference, fallback to English
```bash
python youtube_transcript_downloader.py "https://www.youtube.com/@DuolingoSpanish" --languages es en
```

### Example 4: Download as SRT subtitles to custom directory
```bash
python youtube_transcript_downloader.py "https://www.youtube.com/@crashcourse" --format srt --output course_subtitles
```

## Troubleshooting

**Issue**: "Too Many Requests" error
- **Solution**: Wait a few minutes before retrying. YouTube may temporarily rate-limit requests.

**Issue**: No transcripts found for videos
- **Solution**: Not all videos have transcripts. Try with `--languages en` to include auto-generated English transcripts.

**Issue**: Import errors
- **Solution**: Make sure all dependencies are installed: `pip install -r requirements.txt`

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is provided as-is for educational and personal use.

## Disclaimer

This tool is for personal and educational use only. Please respect YouTube's Terms of Service and content creators' rights. Always ensure you have the right to download and use the transcripts.
