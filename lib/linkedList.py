"""
A python linked list implementation
relying on http://ls.pwd.io/2014/08/singly-and-doubly-linked-lists-in-python/
"""


class Node:

    def __init__(self, data, prev=None, next=None):
        self.data = data
        self.prev = prev
        self.next = next

    def getNextWithValidData(self):
        current = self.next
        while current is not None:
            if current.data is not None:
                return current
            current = current.next

        return None

    def getPrevWithValidData(self):
        current = self.prev
        while current is not None:
            if current.data is not None:
                return current
            current = current.prev

        return None


class LinkedList:

    def __init__(self):
        self.first = None  # head
        self.last = None  # tail
        self.__list = None

    def append(self, data):
        new_node = Node(data, None, None)
        if self.first is None:
            self.first = self.last = new_node
            self.__list = list()
        else:
            new_node.prev = self.last
            new_node.next = None
            self.last.next = new_node
            self.last = new_node

        self.__list.append(new_node)

    def getAsList(self):
        ret = list()
        current = self.first
        while current is not None:
            ret.append(current)
            current = current.next

        return ret
