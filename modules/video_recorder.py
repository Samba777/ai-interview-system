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
        print("✅ VideoFrameCollector initialized!")
        self.frames = []
        self.frame_count = 0
    
    def recv(self, frame):
        """Called for each video frame"""
        try:
            print(f"🎥 recv() called - frame_count: {self.frame_count}")
            
            # Convert frame to numpy array
            img = frame.to_ndarray(format="bgr24")
            print(f"✅ Frame converted - shape: {img.shape}")
            
            # Store frame (limit to 150)
            if len(self.frames) < 150:
                self.frames.append(img.copy())
                print(f"✅ Frame stored - total frames: {len(self.frames)}")
            
            self.frame_count += 1
            
            # CRITICAL FIX: Must return av.VideoFrame for proper rendering
            return av.VideoFrame.from_ndarray(img, format="bgr24")
        except Exception as e:
            print(f"❌ Error in recv: {e}")
            import traceback
            traceback.print_exc()
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
    
    # Initialize session state for this component
    if f"{key}_initialized" not in st.session_state:
        st.session_state[f"{key}_initialized"] = True
    
    try:
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
                frame_count = len(ctx.video_processor.frames)
                st.caption(f"Captured {frame_count} frames")
        
        elif ctx.state.signalling:
            st.warning("⏳ Connecting to camera... Please wait")
        
        else:
            st.info("👆 Click START to begin recording")
        
        # Return frames when stopped
        if not ctx.state.playing and ctx.video_processor:
            frames = ctx.video_processor.frames
            if len(frames) > 0:
                st.success(f"✅ Recorded {len(frames)} frames!")
                return frames
    
    except Exception as e:
        st.error(f"Video recorder error: {str(e)}")
        st.info("Please refresh the page and try again")
    
    return None