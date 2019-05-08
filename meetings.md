# Meetings notes

## Meeting 1.
* **DATE: 11.02.2019**
* **ASSISTANTS: Iván Sánchez Milara**
* **GRADE:** *To be filled by course staff*

### Minutes
 - The meeting took about 20 minutes.
 - The teacher guided us on our faulty parts. He was vey helpful pointing which parts we need to fix.

### Action points
 - In the first question of deadline,
 	- There is a function called 'Data Push and Collection'. This function is ambigious and does not tell what it does.
 	- Also, there are some parts concerning a website. This deadline and application is about an API, we should not mention any website. We should only think on the API.
 - In the second question of deadline,
 	- There are some parts concerning a possible GUI. Again, designin a GUI is not a part of what we do.
 	- An answer box should have only one type of answer, and it should be string.
 	- Statistics are too much detailed. This makes things harder. We should only return answers as statistics. The further calculations can be implemented as extra work.
 	- User authentication, login and registration makes things more complicated. Those features should be removed. The further implementation can be done as extra work.
 	- A question should have an answer resource.
 - In the third question of deadline,
 	- There is a function called 'Automatic Scoring'. This is not a function of our API. It can be implemented using an external service as extra work.
 - In the fourth question of deadline,
 	- There is an example taken and translated from the internet, there should be a reference to this information.
 	- The classification of the API is missing.
 	- Also, there should be a better example of API usage.
 - In general,
 	- In all the deadlines, there is an estimated hours section. We should use this as how much time we spent in hours, not to put deadlines.

### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Meeting 2.
* **DATE: 26.02.2019**
* **ASSISTANTS: Iván Sánchez Milara**
* **GRADE:** *To be filled by course staff*

### Minutes
 - The meeting took about 30 minutes.
 - The teacher made some suggestions to make the application more usable.
 - The teacher had some suggesetions on creating new details in the application.

### Action points
 - In the first question of deadline (Database Design),
    - We need to create a table which will hold some sort of session log. We can call this table questionnaire-instance or session.
    - This table will be used for retrieving the answers from one person. Otherwise, it is not clear which answer belongs to which user.
    - This table should basically include questionnaire-id and answer-id.
    - Also, in question table, attribute 'Title' looks a bit ambigious. We could rename it, but this is not mandatory.

 - In the third question of deadline (Database Testing),
    - We also need testing in an edge case. We can try testing to break nullable attributes.

 - In general,
    - The documentation in both wiki and in the project is neat and enough. We have good documentation in the application.
    - Meeting notes are hold clear and good.
    - We need to mention the usage of sqlite in README file.
    - Also, the SQL dump is missing. It should be added to the repository.

### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Meeting 3.
* **DATE: 28.03.2019**
* **ASSISTANTS: Iván Sánchez Milara**
* **GRADE:** *To be filled by course staff*

### Minutes
 - The meeting took about 30 minutes.
 - The teacher made some suggestions to imporve the design of our resources.
 - The teacher had some suggesetions on changing some details in the documentation of our API.
 - The teacher taught us some ways to locate the resource.

### Action points
 - In the first question of deadline (Resources and relations),
    - Some relations such as "questionnaire-with" are misleading, we should make them more clear.
    - Some relations suah as "question-of" and "answer-to" are wrong, we should change them to "collection".
    - "Answer of one user" and "Answer of one user to one questionnaire" are two resources having unclear relations with other resources, we can remove these two resources or find some new and correct relations.
    - The "Entry point" is missing, we should add an entry point which leads to a collection of all of the questionnaires.

- In the third question of deadline (API design),
    - In the documentation of API, all of the relations should be shown in the state diagram, we should check it.
    - We should use some existing urls as the href for profiles.
    - We should add more error responses for each function.
    - We can change the "mumeta" in "@namespaces", but it is not mandatory.

- In the last question of deadline (REST conformance),
    - We should give more examples of our API to make the conformance justified.

- In general,
    - The documentation in both wiki and in the project is neat and enough. And we have enough amounts of resources.
    - Meeting notes are hold clear and good.

### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Meeting 4.
* **DATE: 26.04.2019**
* **ASSISTANTS: Mika**
* **GRADE:** *To be filled by course staff*

### Minutes
 - The meeting took about 30 minutes.
 - The teacher made some suggestions to imporve the code of API implementation.
 - The teacher had some suggesetions on providing a coverage of the test.
 

### Action points
- In the second question of deadline (Resources implementation),
    - We should use api.url_for() instead of .format() to determine the location of resources, because if there are some changes of the urls in the future, we do not need to change too much codes by using .url_for().
    - We should change some error codes which does not present 'Not Found' to 404.
    - We can put all api.add_resource() at bottom as a url map.
    - In some retrieves, we should include more parameters, which can reduce wrong situations.
    - We should set the default value for parameter 'description', so we can avoid some keyErrors and repeated actions.
    - We should improve the function 'delete'.

- In the third question of deadline (RESTful API testing),
    - We should use the following code to provide a coverage of the test, which has more detailed information.
    ```python
    pytest --cpv-report term-missing --cov=app
    ```
    - The report is extracted and can be found in this [link](https://github.com/exchangeteam/SurveyPWP/blob/master/resources/deadline4/pytest_coverage_report.png)
    
### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

## Midterm meeting
* **DATE:**
* **ASSISTANTS:**
* **GRADE:** *To be filled by course staff*

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*


### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*


## Final meeting
* **DATE:**
* **ASSISTANTS:**
* **GRADE:** *To be filled by course staff*

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*


### Comments from staff
*ONLY USED BY COURSE STAFF: Additional comments from the course staff*

