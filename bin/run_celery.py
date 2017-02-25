#! /usr/bin/env python
import _mypath  # noqa

if __name__ == "__main__":
    from app.tasks import app

    worker = app.Worker(include=["app.tasks"])
    worker.start()
