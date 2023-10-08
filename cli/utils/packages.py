BUILDABLE_PACKAGES = [
    "client",
    "server",
    "worker",
]

RUNNABLE_PACKAGES = [
    *BUILDABLE_PACKAGES,
    "middleware",
]

PACKAGES = [
    *RUNNABLE_PACKAGES,
    "lib",
]
