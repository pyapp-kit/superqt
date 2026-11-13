# Showing exceptions in a dialog

`exceptions_as_dialog` is a context manager that catches exceptions raised in
its block, and shows them in a `QMessageBox` (or a `QErrorMessage`, which lets
the user hide messages they've seen), instead of letting them propagate.

::: superqt.utils.exceptions_as_dialog
