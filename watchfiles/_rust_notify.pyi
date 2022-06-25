from typing import Any, List, Literal, Optional, Protocol, Set, Tuple, Union

__all__ = 'RustNotify', 'WatchfilesRustInternalError'

__version__: str
"""Gets the package version as defined in `Cargo.toml`, modified to match python's versioning semantics."""

class AbstractEvent(Protocol):
    def is_set(self) -> bool: ...

class RustNotify:
    """
    Interface to the Rust [notify](https://crates.io/crates/notify) crate which does
    the heavy lifting of watching for file changes and grouping them into events.
    """

    def __init__(self, watch_paths: List[str], debug: bool, force_polling: bool, poll_delay_ms: int) -> None:
        """
        Create a new RustNotify instance and start a thread to watch for changes.

        `FileNotFoundError` is raised if one of the paths does not exist.

        Args:
            watch_paths: file system paths to watch for changes, can be directories or files
            debug: if true, print details about all events to stderr
            force_polling: if true, always use polling instead of file system notifications
            poll_delay_ms: delay between polling for changes, only used if `force_polling=True`
        """
    def watch(
        self,
        debounce_ms: int,
        step_ms: int,
        timeout_ms: int,
        stop_event: Optional[AbstractEvent],
    ) -> Union[Literal['signal', 'stop', 'timeout'], Set[Tuple[int, str]]]:
        """
        Watch for changes and return a set of `(event_type, path)` tuples.

        This method will wait indefinitely for changes, but once a change is detected,
        it will group changes and return in no more than `debounce_ms` milliseconds.

        The GIL is released during a `step_ms` sleep on each iteration to avoid
        blocking other threads.

        Args:
            debounce_ms: maximum time in milliseconds to group changes over before returning.
            step_ms: time to wait for new changes in milliseconds, if no changes are detected
                in this time, and at least one change has been detected, the changes are yielded.
            timeout_ms: maximum time in milliseconds to wait for changes before returning,
                `0` means wait indefinitely, `debounce_ms` takes precedence over `timeout_ms` once
                a change is detected.
            stop_event: event to check on every iteration to see if this function should return early.

        Returns:
            Either a set of `(event_type, path)` tuples
            (the event types are ints which match [`Change`][watchfiles.Change]),
            `'signal'` if a signal was received, `'stop'` if the `stop_event` was set,
            or `'timeout'` if `timeout_ms` was exceeded.
        """
    def __enter__(self) -> 'RustNotify':
        """
        Does nothing, but allows `RustNotify` to be used as a context manager.

        Note: the watching thead is created when an instance is initiated, not on
        `__enter__`.
        """
    def __exit__(self, *args: Any) -> None:
        """
        Calls close.
        """
    def close(self) -> None:
        """
        Stops the watching thread. After `close` is called, the RustNotify instance can no
        longer be used, calls to [`watch`][watchfiles.RustNotify.watch] will raise a `RuntimeError`.

        Note: `close` is not required, just deleting the `RustNotify` instance will kill the thread
        implicitly.

        As per samuelcolvin/watchfiles#163 `close()` is only required because in the
        event of an error, the traceback in `sys.exc_info` keeps a reference to `watchfiles.watch`'s
        frame, so you can't rely on the `RustNotify` object being deleted, and thereby stopping
        the watching thread.
        """

class WatchfilesRustInternalError(RuntimeError):
    """
    Raised when RustNotify encounters an unknown error.

    If you get this a lot, please file a bug in github.
    """
