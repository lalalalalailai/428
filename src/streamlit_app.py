# -*- coding: utf-8 -*-
"""
Streamlit Cloud Safe Entry Point
=====================================
Wraps app.py with robust error handling for cloud deployment.
Prevents '1ST' (no response) errors by catching all startup exceptions.
"""
import sys
import os
import traceback

def main():
    try:
        import streamlit as st
        
        # Safe path setup - never crash on chdir
        _src_dir = os.path.dirname(os.path.abspath(__file__))
        if _src_dir not in sys.path:
            sys.path.insert(0, _src_dir)
        try:
            os.chdir(_src_dir)
        except Exception:
            pass  # chdir failure is non-fatal
        
        # Import and run main app
        from app import *
        
    except ImportError as e:
        import streamlit as st
        st.error(f"Import Error: {e}")
        st.code(traceback.format_exc())
    except Exception as e:
        import streamlit as st
        st.error(f"Startup Error: {e}")
        st.code(traceback.format_exc())

if __name__ == '__main__':
    main()
