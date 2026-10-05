# Todo List

As a user, I want to manage a simple list of tasks from the command line so that I can keep track of what I need to do.

## Acceptance criteria

- Create: a new task receives a unique id, has status `open`, and displays its id, title, and status. Repeating a no-op produces a clear message; an invalid or unknown id produces a clear error.
- View: tasks are shown in creation order. An empty list prints a clear empty-list message.
- Complete: an open task changes to `done`. Completing an already-done task prints a no-op message. An unknown id produces a clear error and no change.
- Reopen: a done task changes to `open`. Reopening an already-open task prints a no-op message. An unknown id produces a clear error.
- Delete: a task is removed. An unknown id produces a clear error.

## Notes

- Build a small Python command-line application.
- Task titles are free text.
