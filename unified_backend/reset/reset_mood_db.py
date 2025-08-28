from database import Base, engine
import models   # ✅ just import whole models file

# Drop all tables
Base.metadata.drop_all(bind=engine)

# Recreate tables
Base.metadata.create_all(bind=engine)

print("Mood DB has been reset successfully!")
