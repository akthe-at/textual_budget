from textual_serve.server import Server


def main() -> None:
    server = Server("python app.py")
    server.serve()

    if __name__ == "__main__":
        main()
