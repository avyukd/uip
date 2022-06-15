class InvalidParameterException(Exception):
    def __init__(self, message):
        self.message = message

class MustSpecifyValuationTechnique(Exception):
    def __init__(self, message):
        self.message = message

class NoOptionsFoundForTicker(Exception):
    def __init__(self, message):
        self.message = message