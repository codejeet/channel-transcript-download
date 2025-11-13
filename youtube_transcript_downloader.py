#!/usr/bin/env python3
"""
YouTube Channel Transcript Downloader

This script downloads transcripts for all videos from a YouTube channel.
It uses the youtube-transcript-api library to fetch transcripts and
scrapetube to get all videos from a channel without requiring API keys.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs

try:
    import scrapetube
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
        RequestBlocked
    )
except ImportError as e:
    print(f"Error: Missing required dependency: {e}")
    print("\nPlease install required packages:")
    print("pip install -r requirements.txt")
    sys.exit(1)


class YouTubeTranscriptDownloader:
    """Downloads transcripts from all videos in a YouTube channel."""

    def __init__(self, output_dir: str = "transcripts", language_codes: Optional[List[str]] = None, force_download: bool = False):
        """
        Initialize the transcript downloader.

        Args:
            output_dir: Directory to save transcripts
            language_codes: List of preferred language codes (e.g., ['en', 'es'])
            force_download: If True, re-download even if transcript exists
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.language_codes = language_codes or ['en']
        self.force_download = force_download

        # Setup logging
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('YouTubeTranscriptDownloader')
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)

        # File handler
        log_file = self.output_dir / 'download.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    def extract_channel_id(self, channel_url: str) -> str:
        """
        Extract channel ID from various YouTube URL formats.

        Args:
            channel_url: YouTube channel URL

        Returns:
            Channel ID or handle

        Raises:
            ValueError: If URL format is invalid
        """
        parsed_url = urlparse(channel_url)
        path_parts = parsed_url.path.strip('/').split('/')

        # Handle different URL formats:
        # youtube.com/channel/CHANNEL_ID
        # youtube.com/@handle
        # youtube.com/c/CustomName
        # youtube.com/user/Username

        if 'channel' in path_parts:
            idx = path_parts.index('channel')
            if idx + 1 < len(path_parts):
                return path_parts[idx + 1]
        elif path_parts and path_parts[0].startswith('@'):
            return path_parts[0]
        elif 'c' in path_parts:
            idx = path_parts.index('c')
            if idx + 1 < len(path_parts):
                return path_parts[idx + 1]
        elif 'user' in path_parts:
            idx = path_parts.index('user')
            if idx + 1 < len(path_parts):
                return path_parts[idx + 1]

        raise ValueError(f"Could not extract channel identifier from URL: {channel_url}")

    def get_channel_videos(self, channel_identifier: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all videos from a channel.

        Args:
            channel_identifier: Channel ID or handle
            limit: Maximum number of videos to fetch (None for all)

        Returns:
            List of video dictionaries with metadata
        """
        self.logger.info(f"Fetching videos from channel: {channel_identifier}")

        videos = []

        try:
            # Determine if it's a channel ID or handle
            if channel_identifier.startswith('@'):
                # Handle format
                video_generator = scrapetube.get_channel(channel_username=channel_identifier.lstrip('@'))
            elif channel_identifier.startswith('UC'):
                # Channel ID format
                video_generator = scrapetube.get_channel(channel_id=channel_identifier)
            else:
                # Try as channel URL or custom name
                video_generator = scrapetube.get_channel(channel_url=channel_identifier)

            for video in video_generator:
                video_id = video.get('videoId')
                if not video_id:
                    continue

                video_info = {
                    'video_id': video_id,
                    'title': video.get('title', {}).get('runs', [{}])[0].get('text', 'Unknown'),
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                }

                videos.append(video_info)
                self.logger.debug(f"Found video: {video_info['title']} ({video_id})")

                if limit and len(videos) >= limit:
                    break

        except Exception as e:
            self.logger.error(f"Error fetching videos: {e}")
            raise

        self.logger.info(f"Found {len(videos)} videos")
        return videos

    def _get_transcript_filename(self, video_id: str, video_title: str, format: str = 'json') -> Path:
        """
        Get the expected filename for a transcript.

        Args:
            video_id: YouTube video ID
            video_title: Video title
            format: Output format ('json', 'txt', or 'srt')

        Returns:
            Path to the transcript file
        """
        # Sanitize filename
        safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:100]  # Limit length
        base_filename = f"{video_id}_{safe_title}"

        extension = format
        return self.output_dir / f"{base_filename}.{extension}"

    def transcript_exists(self, video_id: str, video_title: str, format: str = 'json') -> bool:
        """
        Check if a transcript file already exists.

        Args:
            video_id: YouTube video ID
            video_title: Video title
            format: Output format to check

        Returns:
            True if transcript file exists
        """
        filepath = self._get_transcript_filename(video_id, video_title, format)
        return filepath.exists()

    def download_transcript(self, video_id: str, video_title: str) -> Optional[Dict]:
        """
        Download transcript for a single video.

        Args:
            video_id: YouTube video ID
            video_title: Video title (for logging)

        Returns:
            Dictionary with transcript data or None if failed
        """
        try:
            # Try to get transcript in preferred languages
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Try to find transcript in preferred languages
            transcript = None
            for lang_code in self.language_codes:
                try:
                    transcript = transcript_list.find_transcript([lang_code])
                    break
                except NoTranscriptFound:
                    continue

            # If no preferred language found, try to get any available transcript
            if transcript is None:
                try:
                    transcript = transcript_list.find_generated_transcript(self.language_codes)
                except NoTranscriptFound:
                    # Get any available transcript
                    available_transcripts = list(transcript_list)
                    if available_transcripts:
                        transcript = available_transcripts[0]
                    else:
                        raise NoTranscriptFound(video_id, [], {})

            # Fetch the transcript data
            transcript_data = transcript.fetch()

            # Convert transcript snippets to dictionaries for JSON serialization
            transcript_list = []
            for snippet in transcript_data:
                transcript_list.append({
                    'text': snippet['text'],
                    'start': snippet['start'],
                    'duration': snippet['duration']
                })

            result = {
                'video_id': video_id,
                'title': video_title,
                'language': transcript.language,
                'language_code': transcript.language_code,
                'is_generated': transcript.is_generated,
                'transcript': transcript_list
            }

            self.logger.info(f"✓ Downloaded transcript for: {video_title} ({transcript.language_code})")
            return result

        except TranscriptsDisabled:
            self.logger.warning(f"✗ Transcripts disabled for: {video_title}")
        except NoTranscriptFound:
            self.logger.warning(f"✗ No transcript found for: {video_title}")
        except VideoUnavailable:
            self.logger.warning(f"✗ Video unavailable: {video_title}")
        except RequestBlocked:
            self.logger.error(f"✗ Too many requests or IP blocked. Please wait before retrying.")
            raise
        except Exception as e:
            self.logger.error(f"✗ Error downloading transcript for {video_title}: {e}")

        return None

    def save_transcript(self, transcript_data: Dict, format: str = 'json') -> None:
        """
        Save transcript to file.

        Args:
            transcript_data: Transcript data dictionary
            format: Output format ('json', 'txt', or 'srt')
        """
        video_id = transcript_data['video_id']
        video_title = transcript_data['title']

        # Use helper method to get filepath
        filepath = self._get_transcript_filename(video_id, video_title, format)

        if format == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, indent=2, ensure_ascii=False)

        elif format == 'txt':
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Title: {transcript_data['title']}\n")
                f.write(f"Video ID: {transcript_data['video_id']}\n")
                f.write(f"Language: {transcript_data['language']} ({transcript_data['language_code']})\n")
                f.write(f"URL: https://www.youtube.com/watch?v={transcript_data['video_id']}\n")
                f.write("=" * 80 + "\n\n")

                for entry in transcript_data['transcript']:
                    f.write(f"{entry['text']}\n")

        elif format == 'srt':
            with open(filepath, 'w', encoding='utf-8') as f:
                for idx, entry in enumerate(transcript_data['transcript'], 1):
                    start_time = self._format_timestamp(entry['start'])
                    end_time = self._format_timestamp(entry['start'] + entry['duration'])

                    f.write(f"{idx}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{entry['text']}\n\n")

        self.logger.debug(f"Saved transcript to: {filepath}")

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to SRT timestamp format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def download_channel_transcripts(
        self,
        channel_url: str,
        format: str = 'json',
        limit: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Download all transcripts from a channel.

        Args:
            channel_url: YouTube channel URL
            format: Output format ('json', 'txt', or 'srt')
            limit: Maximum number of videos to process

        Returns:
            Dictionary with statistics
        """
        self.logger.info(f"Starting transcript download from: {channel_url}")
        self.logger.info(f"Output directory: {self.output_dir.absolute()}")
        self.logger.info(f"Output format: {format}")
        if not self.force_download:
            self.logger.info(f"Cache enabled: Skipping already downloaded transcripts")

        stats = {
            'total_videos': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': datetime.now()
        }

        try:
            # Extract channel identifier
            channel_id = self.extract_channel_id(channel_url)

            # Get all videos
            videos = self.get_channel_videos(channel_id, limit)
            stats['total_videos'] = len(videos)

            if not videos:
                self.logger.warning("No videos found in channel")
                return stats

            # Download transcripts
            for idx, video in enumerate(videos, 1):
                self.logger.info(f"Processing video {idx}/{len(videos)}: {video['title']}")

                # Check if transcript already exists (caching)
                if not self.force_download and self.transcript_exists(video['video_id'], video['title'], format):
                    self.logger.info(f"⊙ Skipping (already exists): {video['title']}")
                    stats['skipped'] += 1
                    continue

                transcript_data = self.download_transcript(video['video_id'], video['title'])

                if transcript_data:
                    self.save_transcript(transcript_data, format)
                    stats['successful'] += 1
                else:
                    stats['failed'] += 1

            # Summary
            stats['end_time'] = datetime.now()
            stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()

            self.logger.info("\n" + "=" * 80)
            self.logger.info("DOWNLOAD SUMMARY")
            self.logger.info("=" * 80)
            self.logger.info(f"Total videos: {stats['total_videos']}")
            self.logger.info(f"Successfully downloaded: {stats['successful']}")
            self.logger.info(f"Skipped (cached): {stats['skipped']}")
            self.logger.info(f"Failed: {stats['failed']}")
            self.logger.info(f"Duration: {stats['duration']:.2f} seconds")
            self.logger.info(f"Output directory: {self.output_dir.absolute()}")
            self.logger.info("=" * 80)

        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            raise

        return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Download transcripts from all videos in a YouTube channel',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all transcripts from a channel
  %(prog)s "https://www.youtube.com/@username"

  # Download transcripts in specific languages
  %(prog)s "https://www.youtube.com/@username" --languages en es fr

  # Save as plain text format
  %(prog)s "https://www.youtube.com/@username" --format txt

  # Limit to first 10 videos
  %(prog)s "https://www.youtube.com/@username" --limit 10

  # Specify custom output directory
  %(prog)s "https://www.youtube.com/@username" --output my_transcripts

  # Force re-download (ignore cache)
  %(prog)s "https://www.youtube.com/@username" --force
        """
    )

    parser.add_argument(
        'channel_url',
        help='YouTube channel URL (e.g., https://www.youtube.com/@username)'
    )

    parser.add_argument(
        '-o', '--output',
        default='transcripts',
        help='Output directory for transcripts (default: transcripts)'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['json', 'txt', 'srt'],
        default='json',
        help='Output format (default: json)'
    )

    parser.add_argument(
        '-l', '--languages',
        nargs='+',
        default=['en'],
        help='Preferred language codes (default: en)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum number of videos to process'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-download even if transcript already exists (ignore cache)'
    )

    args = parser.parse_args()

    # Create downloader
    downloader = YouTubeTranscriptDownloader(
        output_dir=args.output,
        language_codes=args.languages,
        force_download=args.force
    )

    if args.verbose:
        downloader.logger.setLevel(logging.DEBUG)

    # Download transcripts
    try:
        stats = downloader.download_channel_transcripts(
            channel_url=args.channel_url,
            format=args.format,
            limit=args.limit
        )

        # Exit with appropriate code
        if stats['successful'] == 0:
            sys.exit(1)
        elif stats['failed'] > 0:
            sys.exit(2)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
