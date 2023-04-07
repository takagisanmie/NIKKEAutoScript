from functools import cached_property

from module.base.resource import Resource


class Template(Resource):
    def __init__(self, file):
        """
        Args:
            file (dict[str], str): Filepath of template file.
        """
        self.raw_file = file
        self._image = None
        self._image_binary = None

        self.resource_add(self.file)

    @cached_property
    def file(self):
        return self.parse_property(self.raw_file)
