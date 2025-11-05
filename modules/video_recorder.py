"""
Real-time Video Recording Module
Uses streamlit-webrtc for continuous video capture
"""

import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
import cv2
import numpy as np


class VideoFrameCollector(VideoProcessorBase):
    """Collects video frames in real-time during recording"""
    
    def __init__(self):
        self.frames = []
        self.frame_count = 0
    
    def recv(self, frame):
        """Called for each video frame"""
        try:
            # Convert frame to numpy array
            img = frame.to_ndarray(format="bgr24")
            
            # Store frame (limit to 150)
            if len(self.frames) < 150:
                self.frames.append(img.copy())
            
            self.frame_count += 1
            
            # Return frame directly (faster - no text overlay)
            return frame
        except Exception as e:
            print(f"Error in recv: {e}")
            return frame


# Better RTC Configuration with multiple STUN servers
RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
        {"urls": ["stun:stun2.l.google.com:19302"]},
        {"urls": ["stun:stun3.l.google.com:19302"]},
    ]
})


def render_video_recorder(key="video"):
    """Render video recording interface"""
    
    st.markdown("**📹 Video Recording:**")
    
    # WebRTC streamer
    ctx = webrtc_streamer(
        key=key,
        video_processor_factory=VideoFrameCollector,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    # Show status with better feedback
    if ctx.state.playing:
        st.success("🔴 Recording... Speak and look at camera!")
        
        if ctx.video_processor:
            st.caption(f"Captured {len(ctx.video_processor.frames)} frames")
    
    elif ctx.state.signalling:
        st.warning("⏳ Connecting to camera... Please wait (10-30 seconds)")
        st.caption("If it takes longer than 30 seconds, try refreshing the page")
    
    else:
        st.info("👆 Click START to begin recording")
    
    # Return frames when stopped
    if not ctx.state.playing and ctx.video_processor and len(ctx.video_processor.frames) > 0:
        frames = ctx.video_processor.frames
        st.success(f"✅ Recorded {len(frames)} frames!")
        return frames
    
    return None