import app.main


class TestMainModule:

    def test_main_imports_cli(self):
        assert hasattr(app.main, "cli")

    def test_cli_is_callable(self):
        assert callable(app.main.cli)
