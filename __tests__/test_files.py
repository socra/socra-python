import socra


class TestFiles:

    def test_basic(self):
        f = socra.File("socra/sandbox/random.py")

        assert f.content is not None
