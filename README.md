# Xbar On-Air Plugin

This plugin for [xbar](https://xbarapp.com/) changes the state of a smart light bulb when you're in a Zoom meeting. It currently works with any Magic Hue bulb supported by [python-magichue](https://github.com/namacha/python-magichue).

## Installation

Since this is a python script with some dependencies, a convenience shell script wrapper is provided:

```bash
git clone https://github.com/drbayer/xbar-plugin-onair.git
cd ~/Library/Application\ Support/xbar/plugins
ln -s YOUR_CLONE/xbar-onair.15s.sh .
```

This wrapper will install dependencies into a virtual environment inside the
cloned repository.

## Configuration

Configuration variables can be found on the xbar menu --> Open plugin.
