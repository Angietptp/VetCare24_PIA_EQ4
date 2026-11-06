"""Despliegue: la URL de la base puede llegar como `postgres://` (Fly.io, Heroku)."""

from vetcare24.infrastructure.base_de_datos import normalizar_url


def test_postgres_se_convierte_a_postgresql():
    assert normalizar_url("postgres://u:p@h:5432/d") == "postgresql://u:p@h:5432/d"


def test_las_demas_urls_no_cambian():
    assert normalizar_url("postgresql://u:p@h/d") == "postgresql://u:p@h/d"
    assert normalizar_url("sqlite:///x.db") == "sqlite:///x.db"
