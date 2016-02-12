# Flask+MongoDB task storage service

This is a simple code test for a selection process.

It is a RESTful API implementing a generic document storage service. It
considers the documents "tasks" by convention (to comply with the spec).

It uses Flask for the HTTP service and MongoDB for the storage.

It uses the Flask development server to expose itself in the port
5000 (more notes below about this).

The app uses "tasks" for the MongoDB collection name and "fmtasks" for the
database name.

The only configuration implemented is a enviroment variable to change the
default MongoDB URI: MONGODB_URI (also explained below).

## Design notes

This application development did some concessions in the design scope:

1. **Docker layering:** The Docker container in this implementation is designed
to be the final Docker layer. If I was planning to use this application in a
production environment, I would not include the ENTRYPOINT, the run
configuration or the EXPOSE. The application itself could be the layer just
before the last one. And the last one would be a nginx server or some other
wsgi server. The reason to simplify the design was that I know is a code test
and it seemed a unnecessary inconvenience to deal with for the test evaluator.
Also, I would have implemented the Flask app itself as a Python package.

2. **REST semantics:** On a real project, a REST library can be used to
implement the more diverse semantics in HTTP interaction with the service. I
have stick to simple methods to avoid dealing with the header management
required for a more strict RESTful API. Also, the HTTP response codes are over
simplified sometimes.

3. **Avoidance of existing implementations:** There are libraries implementing
the exact behavior required for this code test, like Eve Framework. They even
manage the interaction with the database, listings, responses, etc. In a
normal productive environment, Eve by itself can do everything here, much
more, and better. It only needs some models definitions.

4. **Configuration:** The app only needs one configuration parameter, the
MongoDB URI, and its optional. I did a quick implementation using environment
variables but a proper option parser would be advisable in a real project.

## API

  - *Path:* The API exposes the documents and operations under "/task/". When
necessary, the MongoDB hexadecimal id is appended to the path to signify a
particular document.
    - *HTTP Methods:*
    - POST for the "create" operation.
    - GET for the "read" operation.
    - PUT for the "update" operation.
    - DELETE for the "delete" operation.
  - *Data encoding:* The API uses application/json for the Content-Type both for
sending and for receiving. The content for the documents is specified in a
simple json structure. When necesary, the id of the objects is specified in the
path.


    {'content': 'Sample content.'}

  - *Sample requests:* I implemented the application using a TDD approach. You
can find sample requests in the application test suite.

## Docker

The code test specs required the application to be 'dockerized'.

You can find both Docker and Docker Compose definition files. Run the following
command in the repository root folder to deploy the application using Docker
Compose:

    $ docker-compose up

Alternatively, if you do not have Docker Compose installed, you can run the app
providing a MongoDB connection string as a parameter:

    $ docker build -t fmtasks .
    $ docker run fmtasks MONGODB_URI=mongodb://example.com python fmtasks.py
    
Change "mongodb://example.com" for the appropriate URI.

I used "fmtasks" for the image name in the command but you can change it (in
both lines).
