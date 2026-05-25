# picfofo

**picfofo** is a lightweight, automated image hosting tool for Windows. It monitors your clipboard, automatically uploads any copied screenshots to a **Cloudflare R2** bucket (via S3 API), and instantly replaces your clipboard content with a ready-to-use **Markdown link**.

## ✨ Features

- **Automated Upload**: Detects images in your clipboard and uploads them immediately.
- **Instant Link Generation**: Automatically copies the Markdown link (`![image](url)`) back to your clipboard.
- **Cloudflare R2 Ready**: Optimized for Cloudflare R2 using the S3-compatible API.
- **Secure Storage**: Uses the **System Credential Manager** (Windows Credential Manager / macOS Keychain) to store your Secret Key. No plain-text secrets in config files.
- **Multi-language Support**: Supports both **English** and **Simplified Chinese**.
- **System Tray Integration**: Runs quietly in the background with desktop notifications.
- **Cross-platform Core**: Built with Python and PySide6. (Optimized for Windows, compatible with macOS).

## 🚀 Getting Started

### Prerequisites

- A Cloudflare account with R2 enabled.
- A dedicated R2 bucket and an API Token with "Object Read & Write" permissions.

### Installation (from source)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/picfofo.git
   cd picfofo
   ```

2. **Set up the environment**:
   It's recommended to use Conda or venv:
   ```bash
   conda create -n picfofo python=3.10 -y
   conda activate picfofo
   pip install -r requirements.txt
   ```
   *(Note: You can generate requirements.txt using `pip freeze > requirements.txt`)*

3. **Run the application**:
   ```bash
   python src/main.py
   ```

## 🛠️ Configuration

Open the **picfofo** window and fill in your R2 credentials:

- **Endpoint URL**: Your S3 API endpoint (e.g., `https://<account_id>.r2.cloudflarestorage.com`).
- **Access Key & Secret Key**: Generated from Cloudflare R2 API Tokens.
- **Bucket Name**: The name of your R2 bucket.
- **Custom Domain**: (Optional) Your public domain mapped to the bucket.
- **Upload Path**: (Optional) Folder path within the bucket (e.g., `blog/`).

Click **Save Config**, and you're good to go!

## 📦 Packaging

To create a standalone `.exe` for Windows:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name picfofo --collect-all botocore --paths src --add-data "src/assets;assets" --icon "src/assets/picfofo.ico" src/main.py
```

## 🔐 Security

**picfofo** prioritizes your credential safety:
- **No Plain-text Secrets**: Your `Secret Key` is never saved in `config.json`. It is securely stored using the OS-native keyring service.
- **Git Protection**: `config.json` is included in `.gitignore` to prevent accidental leaks.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
