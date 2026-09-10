import pytest

from cipher.config import DEFAULT_MODEL, ConfigError, Settings, _load_dotenv, load_settings


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("CIPHER_MODEL", raising=False)


def write_env(tmp_path, content):
    env_path = tmp_path / ".env"
    env_path.write_text(content, encoding="utf-8")
    return env_path


def test_load_settings_reads_env_file(tmp_path, monkeypatch):
    write_env(tmp_path, "OPENROUTER_API_KEY=abc123\n")
    monkeypatch.chdir(tmp_path)

    settings = load_settings()

    assert settings == Settings(openrouter_api_key="abc123", model=DEFAULT_MODEL)


def test_load_settings_missing_api_key_raises_config_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ConfigError, match="OPENROUTER_API_KEY"):
        load_settings()


def test_cipher_model_overrides_default(tmp_path, monkeypatch):
    write_env(
        tmp_path,
        "OPENROUTER_API_KEY=abc123\nCIPHER_MODEL=some/other-model:free\n",
    )
    monkeypatch.chdir(tmp_path)

    settings = load_settings()

    assert settings.model == "some/other-model:free"


def test_real_environment_wins_over_dotenv_file(tmp_path, monkeypatch):
    write_env(tmp_path, "OPENROUTER_API_KEY=from-dotenv\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", "from-real-env")

    settings = load_settings()

    assert settings.openrouter_api_key == "from-real-env"


def test_load_dotenv_skips_blank_lines_and_comments(tmp_path, monkeypatch):
    env_path = write_env(
        tmp_path,
        "\n# this is a comment\nOPENROUTER_API_KEY=abc123\n",
    )
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    _load_dotenv(env_path)

    import os

    assert os.environ["OPENROUTER_API_KEY"] == "abc123"


def test_load_dotenv_strips_surrounding_quotes(tmp_path, monkeypatch):
    env_path = write_env(tmp_path, 'OPENROUTER_API_KEY="abc123"\n')
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    _load_dotenv(env_path)

    import os

    assert os.environ["OPENROUTER_API_KEY"] == "abc123"


def test_load_dotenv_missing_file_is_a_noop(tmp_path):
    _load_dotenv(tmp_path / "does-not-exist.env")
    # No exception means success — nothing to assert on environment.
