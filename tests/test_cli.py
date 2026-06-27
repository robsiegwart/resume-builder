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
    """Working directory with a flat YAML source folder ready for build."""
    monkeypatch.chdir(tmp_path)
    source = tmp_path / 'my-resume'
    source.mkdir()
    for f in (PKG / 'sample-data').glob('*.yaml'):
        shutil.copy(f, source / f.name)
    return tmp_path


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

def test_init_creates_folder_with_yaml_files(tmp_path, monkeypatch, runner):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ['init'])
    assert result.exit_code == 0
    assert (tmp_path / 'resume').is_dir()
    assert len(list((tmp_path / 'resume').glob('*.yaml'))) > 0


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

def test_build_produces_html_by_default(scaffolded, runner):
    result = runner.invoke(cli, ['build', 'my-resume'])
    assert result.exit_code == 0
    assert (scaffolded / 'dist' / 'my-resume.html').stat().st_size > 0


def test_build_text_theme_produces_txt(scaffolded, runner):
    result = runner.invoke(cli, ['build', 'my-resume', '--theme', 'default-txt'])
    assert result.exit_code == 0
    assert (scaffolded / 'dist' / 'my-resume.txt').stat().st_size > 0
    assert not (scaffolded / 'dist' / 'my-resume.html').exists()


def test_build_overwrites_on_second_run(scaffolded, runner):
    runner.invoke(cli, ['build', 'my-resume'])
    first = (scaffolded / 'dist' / 'my-resume.html').read_text()
    runner.invoke(cli, ['build', 'my-resume'])
    second = (scaffolded / 'dist' / 'my-resume.html').read_text()
    assert first == second


def test_build_name_flag_changes_output_filename(scaffolded, runner):
    result = runner.invoke(cli, ['build', 'my-resume', '--name', 'thornton'])
    assert result.exit_code == 0
    assert (scaffolded / 'dist' / 'thornton.html').is_file()


def test_build_output_flag_changes_output_dir(scaffolded, runner):
    result = runner.invoke(cli, ['build', 'my-resume', '--output', 'out'])
    assert result.exit_code == 0
    assert (scaffolded / 'out' / 'my-resume.html').is_file()


def test_build_dot_uses_folder_name_as_output(scaffolded, runner):
    monkeypatch_chdir = scaffolded / 'my-resume'
    import os; os.chdir(monkeypatch_chdir)
    result = runner.invoke(cli, ['build', '.'])
    assert result.exit_code == 0
    assert (scaffolded / 'my-resume' / 'dist' / 'my-resume.html').is_file()


def test_build_output_contains_name(scaffolded, runner):
    runner.invoke(cli, ['build', 'my-resume'])
    html = (scaffolded / 'dist' / 'my-resume.html').read_text()
    assert 'Margaret Thornton' in html


def test_build_variant_merges_over_base(scaffolded, runner):
    """A variant subfolder overrides only the YAML files it contains."""
    variant = scaffolded / 'my-resume' / 'senior-role'
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
    result = runner.invoke(cli, ['build', 'my-resume', '--variant', 'senior-role'])
    assert result.exit_code == 0
    html = (scaffolded / 'dist' / 'my-resume.html').read_text()
    assert 'Jane Smith' in html
    assert 'Margaret Thornton' not in html
