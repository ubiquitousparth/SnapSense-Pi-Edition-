# SnapSense Technical Architecture

This document provides a high-level overview of the technical components and data flow within the SnapSense application.

### Core Components

The application is built from several decoupled components that work together:

1.  **Frontend (GUI)**:
    * **Framework**: `CustomTkinter` (a modern extension of Python's built-in `Tkinter` library).
    * **Responsibility**: Renders the user interface, captures user input (button clicks, text entry), and displays the image preview and generated caption. It runs in the main application thread.

2.  **Image Acquisition Module**:
    * **Tools**: System-level command-line utilities like `grim`/`slurp` (for Wayland) or `scrot` (for X11).
    * **Responsibility**: Handles the process of capturing screenshots. It is invoked via Python's `subprocess` module. The application also uses `tkinter.filedialog` for local file selection.

3.  **AI Captioning Service**:
    * **Engine**: [Ollama](https://ollama.com/) running as a local server process.
    * **Model**: `moondream`, a lightweight but powerful vision-language model.
    * **Responsibility**: Receives an image (as a base64 encoded string) and a text prompt. It processes the image, generates a descriptive caption, and streams the response back.

4.  **Text-to-Speech (TTS) Module**:
    * **Engine**: `espeak-ng`, a compact, open-source speech synthesizer.
    * **Responsibility**: Converts the final caption string into audible speech, making the content accessible. It is also invoked via the `subprocess` module.

### Data Flow Diagram

The typical workflow for generating a caption from a screenshot is as follows:
