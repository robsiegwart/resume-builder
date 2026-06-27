import shutil
from pathlib import Path

import pytest
import resumepy
from click.testing import CliRunner
from resumepy.cli import cli


PKG = Path(resumepy.__file__).parent


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def scaffolded(tmp_path, monkeypatch):
    """Working directory set up for build tests (independent of init).

    Mirrors the directory layout that resume.py currently expects:
      Resume Data/Default/*.yaml   — source YAML files
      Templates/html/default.html  — HTML theme
      Templates/text/default.txt   — text theme
    """
    monkeypatch.chdir(tmp_path)

    source_default = tmp_path / 'Resume Data' / 'Default'
    source_default.mkdir(parents=True)
    for f in (PKG / 'sample-data').glob('*.yaml'):
        shutil.copy(f, source_default / f.name)

    templates_html = tmp_path / 'Templates' / 'html'
    templates_html.mkdir(parents=True)
    shutil.copy(PKG / 'themes' / 'html' / 'default' / 'default.html', templates_html / 'default.html')

    templates_text = tmp_path / 'Templates' / 'text'
    templates_text.mkdir(parents=True)
    shutil.copy(PKG / 'themes' / 'text' / 'default.txt', templates_text / 'default.txt')

    return tmp_path


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

def test_init_creates_folder_with_yaml_files(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ['init'])
    assert result.exit_code == 0
    resume_dir = tmp_path / 'resume'
    assert resume_dir.is_dir()
    assert len(list(resume_dir.glob('*.yaml'))) > 0


def test_init_accepts_custom_folder_name(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ['init', 'my-resume'])
    assert result.exit_code == 0
    assert (tmp_path / 'my-resume').is_dir()
    assert not (tmp_path / 'resume').exists()


def test_init_skips_existing_folder(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'resume').mkdir()
    (tmp_path / 'resume' / 'sentinel.yaml').write_text('existing: true\n')
    result = runner.invoke(cli, ['init'])
    assert result.exit_code == 0
    assert 'Skipping' in result.output
    assert (tmp_path / 'resume' / 'sentinel.yaml').read_text() == 'existing: true\n'


def test_init_does_not_copy_templates(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    runner.invoke(cli, ['init'])
    assert len(list((tmp_path / 'resume').glob('*.html'))) == 0


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
    assert 'Margaret Thornton' in html


def test_build_variant_merges_over_default(scaffolded, runner):
    """A variant folder with only Header.yaml should override just that section."""
    variant = scaffolded / 'Resume Data' / 'senior-role'
    variant.mkdir()
    (variant / 'Header.yaml').write_text(
        'name: Jane Smith\n'
        'title: Senior Engineer\n'
        'contact info:\n'
        '  address: 456 Oak St, Anytown, MA 01234\n'
        '  cell: (555) 555-0000\n'
        '  email: jane@example.com\n'
        '  web: janesmith.com\n'
    )

    result = runner.invoke(cli, ['build', 'senior-role'])
    assert result.exit_code == 0
    html = (scaffolded / 'dist' / 'senior-role.html').read_text()
    assert 'Jane Smith' in html
    assert 'John Doe' not in html
