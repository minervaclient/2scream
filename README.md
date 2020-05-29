# 2scream
LMS client APIs for submitting assignments and retrieving grades

## Getting Started

Work in progress.

1. Set your credentials in `d2scream/shib_credentials.py`
2. See `d2scream/__init__.py` for the client "API
3. See `demo.py` for an example
4. Current packages required: `bs4 html5lib requests dateutil`

## Basic API design

`dscream.` Login Mechanism `.` Command `.` Formatter

### Login Mechanisms

- `login_saved()`: Credentials in a Python file. Awesome.

### Commands

- `courses()`
- `grades()`
- `assignments()`

Also:
- `using(course)`: Commands are scoped to the specified course

### Formatters

- `json()`

Eventually:
- `csv()`
- `yaml()`
- `text()`, `text_short()`, `text_long()`, `custom()`: For the command-line
- `ics()`: For stuff that can be shoved in a calendar
- `sql()`: So you can shove the data in SQLite
- `visual()`: For timetables only (HTML)

## Roadmap

- [X] Course listings
- [X] Gradebook
- [ ] Assignments
	- [X] Deadlines
	- [ ] Submission
	- [ ] Attached Files
	- [ ] Re-downloading submissions
	- [ ] Feedback
- [X] Content download
- [ ] Documentation
- [ ] Course announcements
- [ ] LRS authentication

