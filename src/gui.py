from __future__ import annotations


def launch_pyflow() -> None:
    """
    Launch the PyFlow GUI.

    Notes:
      - Requires the `PyFlow` package and Qt bindings (`PySide2` or `PySide6`) to be installed.
      - This simple launcher just opens PyFlow's default workspace.
      - IR <-> PyFlow import/export wiring can be added later.
    """
    try:
        # PyFlow provides a simple App wrapper
        from PyFlow.App import PyFlow
    except Exception as exc:
        _hint = (
            "PyFlow is not installed (or Qt bindings missing).\n"
            "Install with:\n"
            "  pip install PyFlow PySide2\n"
            "If you prefer PySide6:\n"
            "  pip install PyFlow PySide6\n"
        )
        raise RuntimeError(_hint) from exc

    # Start the GUI (blocking call until window closes)
    app = PyFlow()
    app.run()
