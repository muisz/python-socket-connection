from app.app import App

def main():
    host = '127.0.0.1'
    port = 8855
    app = App(host, port)

    try:
        app.start()
    except KeyboardInterrupt:
        app.stop()

if __name__ == '__main__':
    main()
