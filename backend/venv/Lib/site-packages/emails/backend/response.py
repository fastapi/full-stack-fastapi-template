# encoding: utf-8


class Response(object):

    def __init__(self, exception=None, backend=None):
        self.backend = backend
        self.set_exception(exception)
        self.from_addr = None
        self.to_addrs = None
        self._finished = False

    def set_exception(self, exc):
        self._exc = exc

    def raise_if_needed(self):
        if self._exc:
            raise self._exc

    @property
    def error(self):
        return self._exc

    @property
    def success(self):
        return self._finished


class SMTPResponse(Response):

    def __init__(self, exception=None, backend=None):

        super(SMTPResponse, self).__init__(exception=exception, backend=backend)

        self.responses = []

        self.esmtp_opts = None
        self.rcpt_options = None

        self.status_code = None
        self.status_text = None
        self.last_command = None
        self.refused_recipient = {}

    def set_status(self, command, code, text, **kwargs):
        self.responses.append([command, code, text, kwargs])
        self.status_code = code
        self.status_text = text
        self.last_command = command

    @property
    def success(self):
        return self._finished and self.status_code and self.status_code == 250

    def __repr__(self):
        return "<emails.backend.SMTPResponse status_code=%s status_text=%s>" % (self.status_code.__repr__(),
                                                                                self.status_text.__repr__())

