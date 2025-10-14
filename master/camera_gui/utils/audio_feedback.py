"""
Audio feedback module for capture events
Provides simple sound notifications on macOS/Linux systems
"""

import subprocess
import logging
import os
from pathlib import Path


class AudioFeedback:
    """Manages audio feedback for capture events"""
    
    def __init__(self):
        self.enabled = True  # Default enabled
        self.sound_file = self._get_default_sound()
        
    def _get_default_sound(self):
        """Get platform-appropriate default sound"""
        # Use project's shutter.wav sound
        # Path from audio_feedback.py (camera_gui/utils/) to shutter.wav (master/)
        sound_file = Path(__file__).parent.parent.parent / "shutter.wav"
        
        if sound_file.exists():
            return str(sound_file)
        
        # Fallback to macOS system sounds if shutter.wav not found
        macos_sounds = [
            '/System/Library/Sounds/Pop.aiff',
            '/System/Library/Sounds/Tink.aiff',
            '/System/Library/Sounds/Glass.aiff'
        ]
        
        for sound in macos_sounds:
            if os.path.exists(sound):
                return sound
                
        # Linux fallback (beep)
        return 'beep'
    
    def play_capture_sound(self):
        """Play capture sound effect (non-blocking)"""
        if not self.enabled:
            return
            
        try:
            if self.sound_file == 'beep':
                # Linux beep fallback
                subprocess.Popen(['beep', '-f', '800', '-l', '100'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:
                # macOS afplay
                subprocess.Popen(['afplay', self.sound_file],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                               
        except Exception as e:
            logging.debug(f"Audio feedback failed: {e}")
            # Silently fail - audio is non-critical
    
    def set_enabled(self, enabled):
        """Enable or disable audio feedback"""
        self.enabled = enabled
        logging.info(f"Audio feedback {'enabled' if enabled else 'disabled'}")


# Global instance
_audio = None

def get_audio_feedback():
    """Get or create global audio feedback instance"""
    global _audio
    if _audio is None:
        _audio = AudioFeedback()
    return _audio

def play_capture_sound():
    """Convenience function to play capture sound"""
    get_audio_feedback().play_capture_sound()

def set_audio_enabled(enabled):
    """Convenience function to enable/disable audio"""
    get_audio_feedback().set_enabled(enabled)
