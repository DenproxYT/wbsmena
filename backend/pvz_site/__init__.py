try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    # Позволяем приложению запускаться даже если pymysql ещё не установлен
    # (например, до пересборки docker-образа).
    pass
