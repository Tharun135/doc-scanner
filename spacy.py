import re

class DummySent:
    def __init__(self, text):
        self.text = text
        self.tokens = []
        
    def __iter__(self):
        return iter(self.tokens)
        
    def __len__(self):
        return len(self.tokens)

class DummyToken:
    def __init__(self, text, idx, sent):
        self.text = text
        self.idx = idx
        self.sent = sent
        self.lemma_ = text.lower()
        self.dep_ = ""
        self.pos_ = ""
        self.tag_ = ""

class DummyDoc:
    def __init__(self, text):
        self.text = text
        # Simple sentence splitting
        raw_sents = [s for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        if not raw_sents and text.strip():
            raw_sents = [text]
        self.sents = [DummySent(s) for s in raw_sents]
        
        self.tokens = []
        for s in self.sents:
            # simple word splitting
            words = re.finditer(r'\b\w+\b', s.text)
            for w in words:
                token = DummyToken(w.group(), w.start(), s)
                self.tokens.append(token)
                s.tokens.append(token)

    def __iter__(self):
        return iter(self.tokens)

    def __len__(self):
        return len(self.tokens)

def load(*args, **kwargs):
    class DummySpacyInstance:
        def __init__(self):
            self.max_length = 3000000
        def __call__(self, text):
            return DummyDoc(text)
    return DummySpacyInstance()
