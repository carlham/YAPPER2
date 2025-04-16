
“Yapper” - Twitter clone Documentation

Project Creators: 
Carl
Sander
Jakub

Github Repo: https://github.com/Jakubo0451/YAPPER
Live site: https://yapper-zwai.onrender.com/
Backend: https://yapper-4qux.onrender.com/ (when you try to use the backend it will have to load the first time, so login and accessing it the first time might be slow, but should work fine after that.) 
(note that you need to make an account in order to use the application and certain endpoints)

Technologies used

User Interface
For our frontend we’ve decided to use react. The reason behind is that it provides a fast, responsive SPA experience and it is widely used in modern web development. We have also used it as an opportunity to learn React and it generally suited our needs.

Processing / API
The “bulk” of the backend of the project has been written in python, specifically we have used the fastAPI python framework. It generally works well with PostgreSQL, it is easy to use and is asynchronous.






API Endpoints are as follows:
1. Tweets
Create a Tweet:


URL: /tweets
Method: POST
Description: Creates a new tweet. Requires authentication (JWT).
Request Body: Should include the tweet's content.
Response: The created tweet object or an error message.
Retrieve All Tweets (List Tweets):


URL: /tweets
Method: GET
Description: Retrieves a list of all tweets.
Query Parameters (Optional):
limit: For pagination (e.g., ?limit=10).
offset: For pagination (e.g., ?offset=20).
Response: A list of tweet objects.
Retrieve a Single Tweet:


URL: /tweets/{tweet_id}
Method: GET
Description: Retrieves a specific tweet by its ID.
Path Parameter: tweet_id (the ID of the tweet).
Response: The tweet object or a 404 (Not Found) error.
Update/Edit a Tweet:


URL: /tweets/{tweet_id}
Method: PUT (or PATCH for partial updates)
Description: Updates an existing tweet. Requires authentication and ownership check.
Path Parameter: tweet_id (the ID of the tweet).
Request Body: The updated tweet content.
Response: The updated tweet object or an error message.
Delete a Tweet:


URL: /tweets/{tweet_id}
Method: DELETE
Description: Deletes a tweet. Requires authentication and ownership check.
Path Parameter: tweet_id (the ID of the tweet).
Response: A success message or a 404 (Not Found) error.
Search for Tweets (by Text):


URL: /tweets/search
Method: GET
Query Parameter: q (the search query, e.g., ?q=hello).
Description: Searches for tweets containing the specified text.
Response: A list of matching tweet objects.
Search for Tweets by Hashtag:


URL: /tweets/hashtags/search
Method: GET
Query Parameter: hashtag (the hashtag to search for, e.g., ?hashtag=python).
Description: Searches for tweets containing the specified hashtag.
Response: A list of matching tweet objects.
2. Accounts (Users)
Create an Account (Register):


URL: /accounts (or /users)
Method: POST
Description: Creates a new user account.
Request Body: Should include username, email, and password.
Response: The created user object or an error message.
Retrieve All Accounts (List Users):


URL: /accounts (or /users)
Method: GET
Description: Retrieves a list of all user accounts.
Query Parameters (Optional):
limit: For pagination (e.g., ?limit=10).
offset: For pagination (e.g., ?offset=20).
Response: A list of user objects.
Retrieve a Single Account (Get User):


URL: /accounts/{user_id} (or /users/{user_id})
Method: GET
Description: Retrieves a specific user by their ID.
Path Parameter: user_id (the ID of the user).
Response: The user object or a 404 (Not Found) error.
Search for an Account (Search Users):


URL: /accounts/search (or /users/search)
Method: GET
Query Parameter: q (the search query, e.g., ?q=jane).
Description: Searches for user accounts matching the specified query.
Response: A list of matching user objects.
Delete a Account (Delete User):


URL: /accounts/delete (or /users/delete)
Method: DELETE
Path Parameter: user_id (the ID of the user).
Description: Deletes users account matching the specified ID. Requires specified user to be logged in. 
Response: A success message or a 404 (NOT FOUND) error
Data Storage:
PostgreSQL was used for data storage, it’s good for structured data like users and tweets and it is also free to host on render. The task also required us to use a relational database.

There were talks of implementing SQL injection prevention, but SQLAlchemy which we used for querying the database prevents this so there was no need to implement it. 



Hosting
We are hosting the entire project on render. All three parts of the project are split up and being hosted there. It’s great because we can host a PostgreSQL DB there for free (for a month...). It is also just extremely easy to use and free. I would also like to mention that the frontend and database are being hosted on one account and the API on another.



Setting it up locally
To set up the project locally you first need to clone the git repository.Then you want to navigate to the /frontend folder and run ‘npm i’ to install dependencies. To run the frontend you want to run ‘npm run start’, at which point the frontend will be up and running locally, connecting to the backend API hosted on Render. 



‘Flow’
User creates an account via the POST /users method. This requires a unique username and a password. We store the hashed password in the database together with the unique username.
User gets redirected to the login page, where they supply the username and password they made. They then get logged in via the /login route, which creates a token and stores it in localstorage for easy access. This token gets accessed when the user tries to edit and delete tweets, to make sure they can only delete and edit their own tweets. 
After logging in the user gets access to see all tweets posted by all users on the page. They can now also post, edit and delete their own tweets. If a tweet is posted by the logged in user, it will have an edit and delete button associated with it. The edit button brings up a text box where you can edit the tweet and tags, and the delete button brings up an alert box asking you if you want to delete the tweet. 
Searching
The user can search for hashtags, accounts and just general text in tweets via the search in the top right on the page
To search for users, start the search with @, example @john will return all users containing the word john
To search for hashtags, start the search with #, example #python and you will get all the tweets containing #python
To search for general text in tweets you don’t need a prefix, you just need to write what you want to search for, for example ‘weather’ to get all tweets containing the word weather. 
When the user is finished using the page, they can choose to log out via the X in the top-right corner. This will redirect you back to the login page.
