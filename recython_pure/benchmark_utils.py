import io
import sys

# from contextlib import contextmanager


class CaptureOutput:
    """Context manager that captures the standard output of a function."""

    def __enter__(self) -> io.StringIO:
        """Enter the runtime context related to this object.

        Returns:
            StringIO: The captured output.
        """
        self.captured_output = io.StringIO()
        self.old_output = sys.stdout
        sys.stdout = self.captured_output
        return self.captured_output

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the runtime context and return a Boolean flagging an exception.

        Args:
            exc_type: The type of the exception.
            exc_val: The value of the exception.
            exc_tb: The traceback of the exception.
        """
        sys.stdout = self.old_output
        self.captured_output.close()


# @contextmanager
# def capture_output() -> io.StringIO:
#     """Context manager that captures the standard output of a function.
#
#     Yields:
#         StringIO: The captured output.
#     """
#     new_output = io.StringIO()
#     old_output = sys.stdout
#     sys.stdout = new_output
#     try:
#         yield new_output
#     finally:
#         sys.stdout = old_output
#         new_output.close()
