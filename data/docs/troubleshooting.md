# Sugar Labs Troubleshooting & FAQ

## Frequently Asked Questions

### What age group is Sugar designed for?
Sugar is designed primarily for children aged 5-12, though it can be used by learners of any age. The interface is intentionally simple and icon-driven to be accessible to young children and those who may not be literate.

### What programming languages does Sugar use?
Sugar itself is written in Python and uses GTK 3 for the graphical interface. Activities are also primarily written in Python using the sugar-toolkit-gtk3 library. Music Blocks and some newer web-based Activities use JavaScript. Turtle Blocks uses a visual block-based language that generates Python code internally.

### How is Sugar different from Scratch?
While both Sugar and Scratch are designed for children's education, they serve different purposes. Scratch is a single programming environment, while Sugar is a complete desktop operating system with many Activities. Sugar includes Turtle Blocks (similar to Scratch) but also word processing, web browsing, collaboration tools, and more. Sugar emphasizes collaboration and journaling as core features.

### Can Sugar run on Windows or macOS?
Sugar is designed for Linux. It does not run natively on Windows or macOS. However, you can run Sugar in a virtual machine (VirtualBox or QEMU) on any operating system. Sugar Live Build provides a bootable ISO image that can run from a USB drive without installing.

## Common Issues

### Sugar won't start after installation
If Sugar fails to start, check the following:
1. Ensure all dependencies are installed: `sudo apt install sucrose`
2. Check for missing GTK libraries: `python3 -c "from gi.repository import Gtk"`
3. Look at logs: `~/.sugar/default/logs/`
4. Try resetting the profile: `rm -rf ~/.sugar`

### Activities not showing in Home View
If installed Activities don't appear:
1. Check the Activities directory: `ls ~/Activities/`
2. Verify the activity.info file exists and is correctly formatted
3. Restart Sugar: log out and log back in
4. Check for Python errors: `sugar-activity3 MyActivity` from terminal

### Journal is full or slow
The Journal stores all data in `~/.sugar/default/datastore/`. If it becomes full:
1. Delete old Journal entries you no longer need
2. Check disk space: `df -h`
3. The datastore uses SQLite and Xapian for indexing. You can rebuild the index by removing `~/.sugar/default/datastore/index/`

### Network collaboration not working
For collaboration features to work:
1. All computers must be on the same local network
2. Sugar uses mDNS (Avahi) for discovery - ensure avahi-daemon is running
3. Check that Telepathy services are running
4. Firewall must allow mDNS (port 5353) and Telepathy connections

### Pippy Activity crashes on launch
1. Ensure Python 3 is the default: `python3 --version`
2. Install missing Python modules: `sudo apt install python3-gi python3-cairo`
3. Check Pippy logs in the Journal or terminal output
4. Try reinstalling: `sudo apt install --reinstall sugar-pippy-activity`
