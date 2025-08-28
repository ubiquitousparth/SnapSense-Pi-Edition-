## Installation Guide

Follow these steps to set up and run **SnapSense** on a Debian-based Linux system.


# Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd snapsense-project
```
# Step 2: Install System Dependencies
```bash
sudo apt update
```

## Install Ollama (see official guide for latest method)
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Install screenshot tools
### For Wayland
```bash
sudo apt install grim slurp -y
```
### For X11
```bash
sudo apt install scrot -y
```

## Install the text-to-speech engine
```bash
sudo apt install espeak-ng -y
```

# Step 3: Set up Ollama and Pull the Model
```bash
ollama pull moondream
```

# Step 4: Set up Python Environment
```bash
sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate
```

# Step 5: Install Python Dependencies
```bash
pip install -r requirements.txt
```

# Step 6: Make the Launcher Script Executable
```bash
chmod +x launch.sh
```

# Step 7: Create a Keyboard Shortcut (Keybinding)
Open Settings → Keyboard → View and Customize Shortcuts <br />
Go to Custom Shortcuts → Add Custom Shortcut
Fill in the following:
1. Name: Launch SnapSense
2. Command:
3. ```bash
   /home/pi/snapsense-project/launch.sh
   ```
4. Shortcut: Ctrl+Alt+S (or any preferred combination)
