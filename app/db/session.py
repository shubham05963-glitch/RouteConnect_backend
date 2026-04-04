from firebase_admin import firestore

def get_db():
    """Dependency that injects the Firestore database client instance."""
    try:
        db = firestore.client()
        yield db
    except Exception as e:
        print(f"Error connecting to Firestore: {e}")
        raise e
