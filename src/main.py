from database import get_engine


engine = get_engine()


try:
    connection = engine.connect()
    print("Connexion réussie à PostgreSQL/PostGIS")
    connection.close()

except Exception as e:
    print("Erreur de connexion :")
    print(e)