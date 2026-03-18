# Sugar Learning Platform Overview

Sugar is a free and open-source desktop environment designed for interactive learning by children. It was originally developed as the user interface for the One Laptop per Child (OLPC) XO laptop. Sugar is now developed and maintained by Sugar Labs, a volunteer-driven nonprofit organization.

## Key Features

Sugar provides a simple, intuitive interface for children aged 5-12. Unlike traditional desktops, Sugar uses a Journal instead of a filesystem. The Journal automatically saves all work and activities, making it easy for children to resume where they left off.

Sugar uses Activities instead of applications. Each Activity is designed to be collaborative, allowing multiple students to work together over the network. Activities are written in Python and use the Sugar Toolkit (sugar-toolkit-gtk3) for integration with the Sugar desktop.

## Architecture

Sugar runs on top of Linux and uses GTK for its graphical interface. The desktop is organized around four views: the Home View (showing the child's activities), the Neighborhood View (showing other users and shared activities), the Group View (showing friends), and the Activity View (the currently running activity).

The Sugar datastore (Journal) stores all artifacts created by the user. Every Activity interacts with the Journal to save and load data. The Journal uses metadata like tags, title, and timestamps to organize entries.

## Supported Platforms

Sugar can be installed on most Linux distributions. The recommended way to try Sugar is through Sugar Live Build, a bootable USB image based on Debian. Sugar also runs on Fedora via the SOAS (Sugar on a Stick) distribution. For Raspberry Pi users, Sugar can be installed on Raspberry Pi OS (Debian-based) using the package manager.

To install Sugar on Debian/Ubuntu:
```bash
sudo apt update
sudo apt install sucrose
```

To install on Fedora:
```bash
sudo dnf install sugar sugar-toolkit-gtk3
```

For Raspberry Pi:
```bash
sudo apt update
sudo apt install sucrose
```
