# WebView Client Server Example

## Description

This demo repository shows how to use a [pywebview](https://pywebview.flowrl.com/) to display a web page.
The `main.py` file starts a server for sending and receiving data from `webview_app.py` client.
Thge `webview_app.py` then starts the webview in a completly different process which isolates the webview from the server process.
In most cases it is not necessary to do this; However, sometimes the are edge cases where you need to send data from the server to the client while running a webview.

This method is useful for running a webview in a separate process from the server and should work cross-platform.

## Setup

Install using Poetry:

```bash
poetry install
```
