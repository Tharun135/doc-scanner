class DummyDoc:
    def __init__(self, text=""):
        self.text = text
        self.sents = []
    
    def __iter__(self):
        return iter([])

def load(*args, **kwargs):
    class DummySpacyInstance:
        def __init__(self):
            self.max_length = 0
        def __call__(self, text):
            return DummyDoc(text)
    return DummySpacyInstance()
