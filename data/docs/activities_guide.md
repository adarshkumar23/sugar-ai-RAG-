# Sugar Activities Guide

## What are Activities?

In Sugar, applications are called "Activities." Every Activity in Sugar is designed with collaboration in mind. Activities can be shared over the network so that multiple children can participate in the same session.

## Popular Activities

### Turtle Blocks
Turtle Blocks (also known as Turtle Art) is a Logo-inspired graphical programming environment. Children snap together visual blocks to create drawings, animations, and interactive art. Turtle Blocks uses Python under the hood and can be extended with custom blocks. It teaches computational thinking, geometry, and basic programming concepts.

To launch Turtle Blocks, click its icon on the Home View or search for it in the Activity List.

### Write Activity
Write is a word processor based on AbiWord. It supports basic text formatting, images, tables, and collaboration. Multiple students can co-edit a document in real-time when the Activity is shared.

### Browse Activity
Browse is a web browser Activity based on WebKit. It allows students to explore the web and save pages to the Journal.

### Pippy
Pippy is a Python programming Activity. Students write Python code and see the output immediately. It includes many example scripts covering graphics, games, sound, and more. Pippy is the recommended starting point for children who want to learn text-based programming in Sugar.

### Calculate Activity
Calculate is a scientific calculator Activity. It supports basic arithmetic, algebra, trigonometry, and graphing functions.

### Chat Activity
Chat allows students to communicate via text messages on the local network. It demonstrates Sugar's collaboration framework.

## Creating a New Activity

To create a new Sugar Activity, you need:
1. Python 3 programming knowledge
2. The sugar-toolkit-gtk3 library
3. An activity.info metadata file
4. A setup.py file for packaging

The basic structure of a Sugar Activity:

```
MyActivity.activity/
├── activity/
│   ├── activity.info
│   └── activity-icon.svg
├── myactivity.py
└── setup.py
```

The `activity.info` file contains metadata:
```ini
[Activity]
name = MyActivity
activity_version = 1
bundle_id = org.sugarlabs.MyActivity
exec = sugar-activity3 myactivity.MyActivity
icon = activity-icon
license = GPLv3+
```

Your main Python file should extend `sugar3.activity.activity.Activity`:

```python
from sugar3.activity import activity
from gi.repository import Gtk

class MyActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        label = Gtk.Label(label="Hello Sugar!")
        self.set_canvas(label)
        self.show_all()
```

To install the Activity for testing:
```bash
cd MyActivity.activity
python3 setup.py dev
```

## Collaboration in Activities

Sugar's collaboration framework uses Telepathy (now often replaced by CollabWrapper). To make an Activity collaborative, you use the CollabWrapper from sugar3.activity:

```python
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3 import network
```

Activities share data using D-Bus Tubes over the network. When a student shares an Activity, others on the same network can see it in the Neighborhood View and join.
