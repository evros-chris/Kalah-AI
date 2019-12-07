class Observable():
    def __init__(self):
        self.__observers = set()
        self.__has_changed = False

    def add_observer(self, observer):
        self.__observers.add(observer)

    def delete_observer(self, observer):
        self.__observers.discard(observer)

    def set_changed(self):
        self.__has_changed = True

    def notify_observers(self, arg):
        if self.__has_changed:
            for observer in self.__observers:
                observer.update(self, arg)
        self.__has_changed = False


class Observer():
    def __init__(self, name):
        self.name = name

    def update(self, source, arg):
        print(f'Received messsage "{arg}" from {source}')
