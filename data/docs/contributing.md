# Contributing to Sugar Labs

## Getting Started as a Developer

Sugar Labs welcomes contributions from developers of all skill levels. The project is hosted on GitHub at https://github.com/sugarlabs. The main repositories include:
- `sugar`: The core desktop environment
- `sugar-toolkit-gtk3`: The Python toolkit for building Activities
- `sugar-datastore`: The Journal backend
- Various Activity repositories (e.g., `turtleart-activity`, `write-activity`)

## Development Setup

### Prerequisites
- Linux (Debian/Ubuntu or Fedora recommended)
- Python 3.6+
- GTK 3.0 development libraries
- Git

### Setting Up the Development Environment

1. Fork the repository on GitHub
2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/sugar.git
cd sugar
```
3. Install dependencies:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
sudo apt install python3-dbus python3-telepathy python3-xapian
```
4. Set up the development environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## Coding Standards

Sugar Labs follows PEP 8 for Python code style. We use flake8 for linting:
```bash
pip install flake8
flake8 src/
```

All code must be compatible with Python 3.6 and above. Use type hints where possible. Write docstrings for all public functions and classes.

## Submitting Changes

1. Create a feature branch: `git checkout -b my-feature`
2. Make your changes and commit with clear messages
3. Push to your fork: `git push origin my-feature`
4. Open a Pull Request on GitHub
5. Wait for review from a maintainer

Pull requests should include:
- A clear description of the changes
- Tests for new functionality
- Updated documentation if applicable
- Screenshots for UI changes

## Communication Channels

- **Matrix**: #sugar on Matrix (chat.sugarlabs.org) is the main real-time communication channel
- **Mailing List**: sugar-devel@lists.sugarlabs.org for development discussions
- **GitHub Issues**: For bug reports and feature requests
- **IRC**: #sugar on Libera.Chat (bridged to Matrix)

## Google Summer of Code

Sugar Labs participates in Google Summer of Code (GSoC) regularly. GSoC is a great way to get involved with Sugar Labs. Past GSoC projects have included new Activities, improvements to the Sugar desktop, Music Blocks enhancements, and developer tooling. Check the Sugar Labs wiki for the latest GSoC ideas page.

## License

All Sugar Labs code is licensed under the GNU General Public License v3 or later (GPLv3+). By contributing, you agree to license your contributions under the same license.
