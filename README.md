## Vaishvik Brahmbhatt vbrahmb2@stevens.edu
## Kush Patel kpatel24@stevens.edu, 
## Rishika Reva Kalakonda rkalakon@stevens.edu

#### GitHub URL: https://github.com/vaishvik24/CS515-Project3-Web_Forum

# CS 515: Project 3 - Web Forum in FLASK 🎮 

##  ⏰ Estimated hours: 42 hours

| Hours |                 Work                  |
|-------|:-------------------------------------:|
| 3     |    planning and managing the tasks    |
| 4     |    reading and understanding flow     |
| 7     |        implementing base flow         |
| 15    |       implementing 5 extensions       |
| 6     |    modification & refactoring code    |
| 5     |   testing code along with bug fixes   |
| 2     | creating README doc and GitHub set up |

##  🧪 Testing

- While implementing the base flow, I tested each function with writing doctests which helped to handle simple error cases. Once the API is ready to be tested, I start the flaks server and hit the request from the postman/curl request just to make sure it returns correct response and results. Even, I added a few more APIs to test overall working. I did testing with more cross cases just to make sure a key is unique and does not get conflicted with another which leads to make data into inconsistent stage.
- Once, we are done with baseflow, we merged our code into a single py file and did testing end-to-end with all extensions. 

## 🐛 Bugs/Issues

- The current final code has no bugs/issues identified during overall manual testing.
- Future improvement: We can have persistent storage which could be file based or any open databases. 

## 💡 Example of issues/bugs and solution for it

- The implementation of baseflow was easy but the user extension took time for us. The post can be deleted by key that could be user key or post key. So, identifying key whether it is post or user key was a time-consuming. Later, we found a catch and the issue got resolved.
- Even, we were stuck into the time based range queries because the input format of date and posted date could be different. Later, we use epoch timestamp which can be converted to any format as per requirements. 
- We tried to write our own postman JSONs for extension but it was a bit difficult to write our own cases. With the reference of the given jsons, we managed to write some testcases JSONs for our extensions.  

## 🧩 Extensions:
We've implemented 5 extensions. 
Postman collection Link: https://api.postman.com/collections/3753695-16d75404-5cc2-43f1-b13f-cbdd160c4fb0?access_key=PMAT-01GZA2XQG0D8N98N798EKCT46X

Each extension is described as below:
### 1. User and User keys
- The conventional flow has a concept of simple posts. But, in order to delete and do more operation per post in future. So, remember key for each post is not a good way for system. So, posts created by a single user can be managed by a user using its private key. This would be given to user while creating of the user (APIs are in extension 2). 
- While creating a post, user id and user key has to be passed. If the user id does not match with user key then it would raise 403 forbidden error. If matched, then it creates a post with user id which can be used later. Even, this user key can be used to delete post as well. Instead of post key, a user key can be used as well.


### 2. User Profiles (CURD operations)
- The service has several end points of create a user, get a user, and update a user.
- Each user entity consists of attributes as below:
  1. user_id: unique identifier to identify a user. This is unique per user and which can be changed or updated later. There are some constrains for username like it should have atleast a char, a number, does not contain a space and special characters etc. 
  2. key: this is the private user key which significance is described in the previous extensions.
  3. phone_num: a mobile number with the country extension
  4. name: full name of the user
  5. city: the location of a user


### 3. User based range queries
- The concept of user is a much useful to manage posts. This is the filter request which filters out the posts based by the user_id. 
- If the user does not exists then it throws 404 not found error. If found, then it returns list of posts for the given user.

### 4. 
### 5.

## 🏃‍Run Guide

- Install python 3 in your machine
- Read README.md file to get more context of the project
- The code is written in `app.py` file.
- The server is based on `flask` framework. First of all, you need to install flaks and other dependencies.
- Postman’s GUI is great for interactive testing; you can also use it to export a file for command-line testing, which will be necessary for us to evaluate your code. You can install the command-line tester by running npm install -g newman; if you’re missing the npm command, you need to install node and npmLinks to an external site. The nvmLinks to an external site and is a popular way to do that. 
  1. `setup.sh` shell script which downloads all dependencies
  2. `run.sh` shell script that starts flaks server at port 5000 (http://127.0.01:5000/ to check whether its running or not)
  3. `test.sh` shell script runs all tests (Make sure `npm` is installed as it uses `newman`)

```shell
  $ ./setup.sh
  $ ./run.sh
```
- Now, open new terminal and run following script to test the given usecases.
- Note: The testcases can be updated/added by changing JSON file given in the same root folder. 
```shell
  $ ./test.sh
```
