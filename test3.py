class Test(object):
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return f"<TestClass name={self._name}>"

    def hello(self):
        print(f"Hello {self._name}!")

    @staticmethod
    def helloworld():
        print(f"Hello World!")
