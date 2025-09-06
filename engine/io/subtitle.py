"""Subtitle formatting utilities for various output formats."""

import json
from typing import List, Dict, Any


class SubtitleFormatter:
    """Formats transcription segments into various subtitle formats."""
    
    def format(self, segments: List[Dict[str, Any]], format_type: str) -> str:
        """
        Format segments into specified subtitle format.
        
        Args:
            segments: List of transcription segments.
            format_type: Output format (srt, vtt, txt, json).
            
        Returns:
            str: Formatted subtitle content.
        """
        if format_type == "srt":
            return self.to_srt(segments)
        elif format_type == "vtt":
            return self.to_vtt(segments)
        elif format_type == "txt":
            return self.to_txt(segments)
        elif format_type == "json":
            return json.dumps(segments, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def to_srt(self, segments: List[Dict[str, Any]]) -> str:
        """
        Convert segments to SRT format.
        
        Args:
            segments: List of transcription segments.
            
        Returns:
            str: SRT formatted content.
        """
        lines = []
        for i, segment in enumerate(segments, 1):
            # Index
            lines.append(str(i))
            
            # Timestamps
            start_time = self._seconds_to_srt_time(segment["start"])
            end_time = self._seconds_to_srt_time(segment["end"])
            lines.append(f"{start_time} --> {end_time}")
            
            # Text
            lines.append(segment["text"])
            
            # Empty line between subtitles
            lines.append("")
        
        return "\n".join(lines)
    
    def to_vtt(self, segments: List[Dict[str, Any]]) -> str:
        """
        Convert segments to WebVTT format.
        
        Args:
            segments: List of transcription segments.
            
        Returns:
            str: WebVTT formatted content.
        """
        lines = ["WEBVTT", ""]
        
        for segment in segments:
            # Timestamps
            start_time = self._seconds_to_vtt_time(segment["start"])
            end_time = self._seconds_to_vtt_time(segment["end"])
            lines.append(f"{start_time} --> {end_time}")
            
            # Text
            lines.append(segment["text"])
            
            # Empty line between subtitles
            lines.append("")
        
        return "\n".join(lines)
    
    def to_txt(self, segments: List[Dict[str, Any]]) -> str:
        """
        Convert segments to plain text format.
        
        Args:
            segments: List of transcription segments.
            
        Returns:
            str: Plain text content.
        """
        lines = []
        for segment in segments:
            lines.append(segment["text"])
        
        return "\n".join(lines)
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """
        Convert seconds to SRT timestamp format (HH:MM:SS,mmm).
        
        Args:
            seconds: Time in seconds.
            
        Returns:
            str: SRT timestamp.
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """
        Convert seconds to WebVTT timestamp format (HH:MM:SS.mmm).
        
        Args:
            seconds: Time in seconds.
            
        Returns:
            str: WebVTT timestamp.
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"