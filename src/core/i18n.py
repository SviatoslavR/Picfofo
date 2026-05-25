class LanguageManager:
    TRANSLATIONS = {
        "zh": {
            "title": "picfofo - 图床同步",
            "endpoint": "Endpoint URL:",
            "access_key": "Access Key:",
            "secret_key": "Secret Key:",
            "bucket": "Bucket Name:",
            "domain": "Custom Domain:",
            "path": "Upload Path:",
            "save": "保存配置",
            "language": "界面语言:",
            "status_monitoring": "正在监控剪贴板...",
            "status_uploading": "正在上传图片...",
            "status_success": "上传成功！链接已复制",
            "status_error_config": "错误: R2 配置不完整",
            "status_error_upload": "上传失败: {error}",
            "tray_show": "显示",
            "tray_quit": "退出",
            "tray_minimized_title": "picfofo",
            "tray_minimized_msg": "程序已最小化到托盘运行",
            "tray_success_msg": "图片上传成功，Markdown 链接已复制",
            "msg_save_success": "配置已保存！",
            "msg_upload_failed": "上传失败"
        },
        "en": {
            "title": "picfofo - Image Sync",
            "endpoint": "Endpoint URL:",
            "access_key": "Access Key:",
            "secret_key": "Secret Key:",
            "bucket": "Bucket Name:",
            "domain": "Custom Domain:",
            "path": "Upload Path:",
            "save": "Save Config",
            "language": "Language:",
            "status_monitoring": "Monitoring clipboard...",
            "status_uploading": "Uploading image...",
            "status_success": "Upload success! Link copied",
            "status_error_config": "Error: R2 config incomplete",
            "status_error_upload": "Upload failed: {error}",
            "tray_show": "Show",
            "tray_quit": "Quit",
            "tray_minimized_title": "picfofo",
            "tray_minimized_msg": "Program minimized to tray",
            "tray_success_msg": "Image uploaded, Markdown link copied",
            "msg_save_success": "Config saved!",
            "msg_upload_failed": "Upload Failed"
        }
    }

    def __init__(self, language="zh"):
        self.language = language if language in self.TRANSLATIONS else "zh"

    def set_language(self, language):
        if language in self.TRANSLATIONS:
            self.language = language

    def get(self, key, **kwargs):
        text = self.TRANSLATIONS[self.language].get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text
