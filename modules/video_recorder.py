"""
Video Recording Module
Real-time video recording using streamlit-webrtc
"""
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import threading


class VideoFrameCollector:
    """
    Collects video frames from WebRTC stream
    """
    
    def __init__(self, max_frames=150):
        self.frames = []
        self.max_frames = max_frames
        self.lock = threading.Lock()
    
    def add_frame(self, frame):
        """Add frame to collection"""
        with self.lock:
            if len(self.frames) < self.max_frames:
                self.frames.append(frame)
    
    def get_frames(self):
        """Get collected frames"""
        with self.lock:
            return self.frames.copy()
    
    def clear(self):
        """Clear frames"""
        with self.lock:
            self.frames = []


def render_video_recorder(key="video_recorder"):
    """
    Render video recorder component
    
    Args:
        key: Unique key for component
    
    Returns:
        list of frames if recording complete, None otherwise
    """
    
    # Initialize frame collector
    if f"collector_{key}" not in st.session_state:
        st.session_state[f"collector_{key}"] = VideoFrameCollector()
    
    collector = st.session_state[f"collector_{key}"]
    
    # Better WebRTC configuration with multiple STUN servers
    rtc_configuration = RTCConfiguration({
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]},
        ]
    })
    
    # Video processor callback
    def video_frame_callback(frame):
        img = frame.to_ndarray(format="bgr24")
        collector.add_frame(img)
        return frame
    
    # Render WebRTC streamer
    st.markdown("**📹 Video Recording**")
    
    try:
        webrtc_ctx = webrtc_streamer(
            key=key,
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc_configuration,
            video_frame_callback=video_frame_callback,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
        
        # Show status
        if webrtc_ctx.state.playing:
            st.success("🔴 Recording... Speak and look at camera!")
            frame_count = len(collector.get_frames())
            st.caption(f"Captured {frame_count} frames")
        
        elif webrtc_ctx.state.signalling:
            st.warning("⏳ Connecting to camera... Please wait")
        
        else:
            st.info("👆 Click START to begin recording")
        
        # Return frames when stopped
        if not webrtc_ctx.state.playing and len(collector.get_frames()) > 0:
            frames = collector.get_frames()
            st.success(f"✅ Video captured! ({len(frames)} frames)")
            return frames
    
    except Exception as e:
        st.error(f"Video error: {str(e)}")
        st.info("Please refresh the page")
    
    return None