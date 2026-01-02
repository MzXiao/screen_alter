# WeChat Alert Integration Guide

This guide explains how to set up and use the WeChat alert feature in Screen Monitor.

## 1. Prerequisites

- A WeChat account.
- The `itchat-uos` library (or `itchat`) must be installed in your environment.
- **IMPORTANT**: Your WeChat account must be able to log in to the WeChat Web version. Some newer WeChat accounts may have restrictions on web login.

## 2. How to Log In

1. Open the Screen Monitor application and log in.
2. In the "Config" (配置) panel, look for the **"WeChat Login" (微信登录)** button (added in the latest update).
3. Click the button. A QR code will appear on your screen (usually in a separate window).
4. Scan the QR code with your mobile WeChat app.
5. Confirm the login on your phone.
6. Once logged in, the application status will update to "WeChat: Logged In" (微信已登录).

## 3. Configuring Recipients

- In the **"WeChat Recipient" (微信接收人)** input field, enter the **Remark Name (备注名)** or **Nickname (昵称)** of the person you want to send alerts to.
- It is highly recommended to use a **Remark Name** to ensure uniqueness and stability.
- You can also send alerts to yourself by entering your own nickname or "filehelper" (文件传输助手).

## 4. How it Works

When the application detects a keyword or a reference image on your screen:
1. It captures a screenshot.
2. It sends a text alert to the configured recipient.
3. It sends the screenshot as an image to the same recipient.

## 5. Troubleshooting

- **QR Code doesn't appear**: Ensure you have an active internet connection. Check the application logs for any `itchat` errors.
- **Login fails**: If your account is restricted from using the Web WeChat, `itchat` will not be able to log in. You may see an error like "Login error: 1203" or similar.
- **Messages not sent**: Verify that the recipient name exactly matches the Remark Name or Nickname in your contacts. Ensure you are still logged in (check the status indicator).
- **macOS Permissions**: On macOS, you may need to grant "Accessibility" and "Screen Recording" permissions to the terminal or Python app for the full experience.

## 6. Security Note

`itchat` operates by emulating the WeChat Web client. Your login credentials are not stored; only a local session token (in `itchat.pkl`) is kept for "hot reload" capability, allowing you to stay logged in after restarts.
