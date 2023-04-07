import threading


def func(ev: threading.Event):
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        type=str,
        help="Host to listen. Default to WebuiHost in deploy setting",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="Port to listen. Default to WebuiPort in deploy setting",
    )
    args, _ = parser.parse_known_args()
    host = args.host or 'localhost'
    port = args.port or 12271

    uvicorn.run("module.webui.app:app", host=host, port=port, factory=True)


if __name__ == '__main__':
    func(None)
