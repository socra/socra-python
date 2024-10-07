class Command:
    """
    Base command, from which other commands inherit.
    """

    def execute(self):
        raise NotImplementedError
