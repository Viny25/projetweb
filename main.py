import data_model as data_model

def main():
    model = data_model.db_web()
    
    # 1. Testez la connexion
    print("Test de connexion à la base...")
    test_conn = data_model.db_fetch("SELECT name FROM sqlite_master WHERE type='table'", all=True)
    print(f"Tables disponibles: {test_conn}")
    
    # 2. Testez list_objet
    print("\nTest list_objet():")
    objets = model.list_objet()
    print(f"Type retourné: {type(objets)}")
    print(f"Nombre d'objets: {len(objets)}")
    print("Détail du premier objet:", objets[2] if objets else "vide")

if __name__ == '__main__':
    main()