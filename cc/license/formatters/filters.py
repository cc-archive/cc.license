
import classes

class Source:

    def __init__(self, work_dict):
        if work_dict is None:
            work_dict = {}
        self.id = 'source_work'
        if work_dict.has_key(self.id):
            self.has_source = True
            self.source = work_dict[self.id]
            # only load template if we need to
            self.tmpl = classes.LOADER.load('source.xml')
            self.source_stream = self.tmpl.generate(source=self.source)
        else:
            self.has_source = False

    def __call__(self, stream):
        for kind, data, pos in stream:
            yield kind, data, pos
        if self.has_source:
            for kind, data, pos in self.source_stream:
                yield kind, data, pos


class Permissions:

    def __init__(self, work_dict):
        if work_dict is None:
            work_dict = {}
        self.id = 'more_permissions_url'
        if work_dict.has_key(self.id):
            self.has_permissions = True
            self.source = work_dict[self.id]
            # only load template if we need to
            self.tmpl = classes.LOADER.load('permissions.xml')
            self.permissions_stream = self.tmpl.generate(permissions=self.source)
        else:
            self.has_permissions = False

    def __call__(self, stream):
        for kind, data, pos in stream:
            yield kind, data, pos
        if self.has_permissions:
            for kind, data, pos in self.permissions_stream:
                yield kind, data, pos
