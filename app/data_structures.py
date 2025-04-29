class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop() if self.items else None

    def is_empty(self):
        return len(self.items) == 0


class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        return self.items.pop(0) if self.items else None

    def is_empty(self):
        return len(self.items) == 0


class MenuList:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def get_all(self):
        return self.items


class CategoryTree:
    def __init__(self):
        self.categories = {}

    def insert(self, category, item):
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(item)

    def traverse(self):
        return self.categories
