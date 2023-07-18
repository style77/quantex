class EventListener:
    def __init__(self):
        self.listeners = {}

    def on(self, event):
        def decorator(func):
            if event not in self.listeners:
                self.listeners[event] = []
            self.listeners[event].append(func)
            return func

        return decorator

    def call(self, event, *args, **kwargs):
        if event in self.listeners:
            for listener in self.listeners[event]:
                listener(*args, **kwargs)
