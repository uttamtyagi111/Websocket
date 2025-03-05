class Mail:
    def __init__(self, _from="", _to="", _subject="", _html_content=""):
        self._from = _from
        self._to = _to
        self._subject = _subject
        self._html_content = _html_content

    def getFrom(self):
        return self._from

    def getTo(self):
        return self._to

    def getSubject(self):
        return self._subject

    def getHtmlContent(self):
        return self._html_content
