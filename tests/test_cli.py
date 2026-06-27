import pytest
from click.testing import CliRunner
from resumepy.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def scaffolded(tmp_path, monkeypatch, runner):
    """Working directory with init already run."""
    monkeypatch.chdir(tmp_path)
    runner.invoke(cli, ['init'])
    return tmp_path


def _output_dir(publish_path):
    """Return the single timestamped subdirectory under Publish/."""
    dirs = list(publish_path.iterdir())
    assert len(dirs) == 1, f"Expected 1 output dir, found {len(dirs)}"
    return dirs[0]


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

def test_init_creates_scaffold(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ['init'])
    assert result.exit_code == 0
    assert (tmp_path / 'Sample Data').is_dir()
    assert (tmp_path / 'Sample Templates').is_dir()
    assert (tmp_path / 'config.ini').is_file()


def test_init_skips_existing_folders(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'Sample Templates').mkdir()
    result = runner.invoke(cli, ['init'])
    assert result.exit_code == 0
    assert 'Skipping' in result.output
    # The folder that didn't exist should still be created
    assert (tmp_path / 'Sample Data').is_dir()


def test_init_skips_existing_config(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'config.ini').write_text('[DEFAULT]\n')
    result = runner.invoke(cli, ['init'])
    assert result.exit_code == 0
    assert 'Skipping' in result.output
    # Original content must be preserved
    assert (tmp_path / 'config.ini').read_text() == '[DEFAULT]\n'


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def test_build_default_produces_html_and_txt(scaffolded, runner):
    result = runner.invoke(cli, ['build', 'Default'])
    assert result.exit_code == 0
    out = _output_dir(scaffolded / 'Publish')
    assert (out / 'Default.html').stat().st_size > 0
    assert (out / 'Default.txt').stat().st_size > 0


def test_build_name_flag_changes_output_filename(scaffolded, runner):
    result = runner.invoke(cli, ['build', 'Default', '--name', 'my_resume'])
    assert result.exit_code == 0
    out = _output_dir(scaffolded / 'Publish')
    assert (out / 'my_resume.html').is_file()
    assert (out / 'my_resume.txt').is_file()


def test_build_default_html_contains_name(scaffolded, runner):
    runner.invoke(cli, ['build', 'Default'])
    out = _output_dir(scaffolded / 'Publish')
    html = (out / 'Default.html').read_text()
    assert 'John Doe' in html


def test_build_custom_variant_merges_over_default(scaffolded, runner):
    """Custom-1 overrides Header.yaml — name should reflect Custom-1's value."""
    result = runner.invoke(cli, ['build', 'Custom-1'])
    assert result.exit_code == 0
    out = _output_dir(scaffolded / 'Publish')
    html = (out / 'Custom-1.html').read_text()
    assert 'John Doe II' in html
    assert 'John Doe' in html  # still present (email etc. shared)
