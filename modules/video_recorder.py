"""
Real-time Video Recording Module
Uses streamlit-webrtc for continuous video capture
"""

import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
import cv2
import numpy as np
from datetime import datetime
import queue
import threading


class VideoFrameCollector(VideoProcessorBase):
    """
    Collects video frames in real-time during recording
    """
    
    def __init__(self):
        self.frames = []
        self.lock = threading.Lock()
        self.max_frames = 150  # Collect max 150 frames (5 sec at 30fps)
    
    def recv(self, frame):
        """
        Called for each video frame
        
        Args:
            frame: Video frame from webcam
        
        Returns:
            frame: Pass-through for display
        """
        # Convert frame to numpy array
        img = frame.to_ndarray(format="bgr24")
        
        # Store frame (thread-safe)
        with self.lock:
            if len(self.frames) < self.max_frames:
                self.frames.append(img.copy())
        
        # Return frame for display
        return av.VideoFrame.from_ndarray(img, format="bgr24")
    
    def get_frames(self):
        """Get collected frames (thread-safe)"""
        with self.lock:
            return self.frames.copy()


# RTC Configuration for WebRTC
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)


def render_video_recorder(key="video"):
    """
    Render real-time video recording interface
    
    Args:
        key: Unique key for component
    
    Returns:
        List of captured frames or None
    """
    
    st.markdown("**📹 Video Recording:**")
    
    # Initialize frame collector in session state
    collector_key = f"{key}_collector"
    if collector_key not in st.session_state:
        st.session_state[collector_key] = VideoFrameCollector()
    
    collector = st.session_state[collector_key]
    
    # WebRTC streamer
    ctx = webrtc_streamer(
        key=key,
        video_processor_factory=lambda: collector,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    # Show status
    if ctx.state.playing:
        st.success("🔴 Recording... Speak and look at camera!")
        
        # Show frame count
        frame_count = len(collector.get_frames())
        st.caption(f"Captured {frame_count} frames")
        
        # Stop button
        if st.button("⏹️ Stop Recording", key=f"{key}_stop"):
            ctx.video_processor.frames = []  # Reset for next recording
    
    else:
        st.info("👆 Click START to begin recording")
    
    # Return frames when stopped
    if not ctx.state.playing and len(collector.get_frames()) > 0:
        frames = collector.get_frames()
        st.success(f"✅ Recorded {len(frames)} frames!")
        
        # Store in session state
        frames_key = f"{key}_frames"
        st.session_state[frames_key] = frames
        
        return frames
    
    # Check if frames exist in session state
    frames_key = f"{key}_frames"
    if frames_key in st.session_state:
        return st.session_state[frames_key]
    
    return None