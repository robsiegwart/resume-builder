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
    assert (tmp_path / 'Sample Data').is_dir()


def test_init_skips_existing_config(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'config.ini').write_text('[DEFAULT]\n')
    result = runner.invoke(cli, ['init'])
    assert result.exit_code == 0
    assert 'Skipping' in result.output
    assert (tmp_path / 'config.ini').read_text() == '[DEFAULT]\n'


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def test_build_default_produces_html_and_txt(scaffolded, runner):
    result = runner.invoke(cli, ['build', 'Default'])
    assert result.exit_code == 0
    dist = scaffolded / 'dist'
    assert (dist / 'Default.html').stat().st_size > 0
    assert (dist / 'Default.txt').stat().st_size > 0


def test_build_overwrites_on_second_run(scaffolded, runner):
    runner.invoke(cli, ['build', 'Default'])
    first = (scaffolded / 'dist' / 'Default.html').read_text()
    runner.invoke(cli, ['build', 'Default'])
    second = (scaffolded / 'dist' / 'Default.html').read_text()
    assert first == second


def test_build_name_flag_changes_output_filename(scaffolded, runner):
    result = runner.invoke(cli, ['build', 'Default', '--name', 'my_resume'])
    assert result.exit_code == 0
    dist = scaffolded / 'dist'
    assert (dist / 'my_resume.html').is_file()
    assert (dist / 'my_resume.txt').is_file()


def test_build_default_html_contains_name(scaffolded, runner):
    runner.invoke(cli, ['build', 'Default'])
    html = (scaffolded / 'dist' / 'Default.html').read_text()
    assert 'John Doe' in html


def test_build_custom_variant_merges_over_default(scaffolded, runner):
    """Custom-1 overrides Header.yaml — name should reflect Custom-1's value."""
    result = runner.invoke(cli, ['build', 'Custom-1'])
    assert result.exit_code == 0
    html = (scaffolded / 'dist' / 'Custom-1.html').read_text()
    assert 'John Doe II' in html
    assert 'John Doe' in html  # still present (email etc. shared)
