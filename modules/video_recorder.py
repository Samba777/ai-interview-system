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
            
            # Draw frame counter on video
            cv2.putText(img, f"Frames: {self.frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Return frame for display
            return av.VideoFrame.from_ndarray(img, format="bgr24")
        except Exception as e:
            print(f"Error in recv: {e}")
            return frame


# RTC Configuration
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)


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
    
    # Show status
    if ctx.state.playing:
        st.success("🔴 Recording... Speak and look at camera!")
        
        if ctx.video_processor:
            st.caption(f"Captured {len(ctx.video_processor.frames)} frames")
    else:
        st.info("👆 Click START to begin recording")
    
    # Return frames when stopped
    if not ctx.state.playing and ctx.video_processor and len(ctx.video_processor.frames) > 0:
        frames = ctx.video_processor.frames
        st.success(f"✅ Recorded {len(frames)} frames!")
        return frames
    
    return None