from database import SessionLocal
from models import UserModel, TweetsModel
from sqlalchemy.exc import SQLAlchemyError
import random
from datetime import datetime, timedelta
import hashlib

# script used while developing
# seeds the database with dummy data to have something to display, if you want to be able to use the page, make a own account

# Sample data
usernames = [
    "john_doe", "tech_guru", "code_master", "coffee_lover",
    "pizza_chef", "travel_addict", "music_fan", "book_worm",
    "night_owl", "early_bird"
]

tweet_contents = [
    "Just finished a great coding session! #programming",
    "Working on a new project, super excited about it! #coding",
    "Learning FastAPI and it's amazing! #webdev #python",
    "Don't forget to take breaks when coding! #healthtips",
    "PostgreSQL is my favorite database system. #database",
    "Reading a fascinating book about AI. #artificialintelligence",
    "Just deployed my app to production! #deployment",
    "Debugging is like being a detective in a crime story. #crime",
    "Remember to commit your code frequently! #git",
    "Python makes life so much easier. #pythonlove",
    "RESTful APIs are the backbone of modern web applications. #restapi",
    "This yap doesn't contain a hashtag!"
]

def get_hash_password(plain_password):
    """Simple password hashing for demo purposes"""
    return hashlib.sha256(plain_password.encode()).hexdigest()

def seed_data():
    db = SessionLocal()
    try:
        # Check if we already have data
        existing_users = db.query(UserModel).count()
        if existing_users > 0:
            print(f"Database already has {existing_users} users. Skipping seeding.")
            return
        
        print("Starting database seeding...")
        
        # Create users
        users = []
        for i, username in enumerate(usernames):
            user = UserModel(
                username=username,
                hashed_password=get_hash_password(f"password{i}"),
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        print(f"Created {len(users)} users")
        
        # Create tweets
        tweet_count = 0
        for user in users:
            # Each user gets 5-15 random tweets
            num_tweets = random.randint(5, 15)
            for _ in range(num_tweets):
                # Select random content
                content = random.choice(tweet_contents)
                
                # Create the tweet
                tweet = TweetsModel(
                    content=content,
                    owner_id=user.id,
                    # Let created_at use the default server value
                )
                db.add(tweet)
                tweet_count += 1
        
        db.commit()
        print(f"Created {tweet_count} tweets")
        print("Database seeding completed successfully!")
        
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error seeding database: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()