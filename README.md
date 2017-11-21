# StatisticsCollector
Python application to upload script into client machine, fetch machine statistics like (CPU, memory usage, uptime) and store it to sqlite DB.

## 1. Instructions to install and configure prerequisites or dependencies.

At the bare minimum you'll need the following for your development environment and little knowledge of linux commands:

1. [Python](http://www.python.org)(Would be good if you have Python 2.7 as I have tested it on Python 2.7)
2. [Sqlite](https://sqlite.org)
2. [RabbitMQ](https://www.rabbitmq.com)(Please download a standalone rabbitmq server for linux. You can easily find it in the given link. After downloading, make sure to start it. All instructions are given in the link. Command for starting: path_to_downloaded_folder/sbin/rabbitmq-server )

#### Local Setup

The following assumes you have all of the recommended tools listed above installed.

#### 1. Download the project zip file:

    Extract the downloaded zip. 
    $ unzip SyedWaseemUllah_SR_Python_SysInfo.zip
    $ cd SyedWaseemUllah_SR_Python_SysInfo/Source

#### 2. Create and initialize virtualenv for the project:

    $ mkdir statscollector_virtualenv
    $ virtualenv statscollector_virtualenv
    $ source statscollector_virtualenv/bin/activate
    $ pip install -r requirements.txt

    During requirements installation if you get error 
    Error "fatal error: 'openssl/opensslv.h' file not found"
    Try upgrading pip "pip install --upgrade pip" and rerun pip install -r requirements.txt

#### 4. Run the tests:

    $ nosetests tests -v (nose doesn't run tests if you have set execute permission on file)

#### 3. Run the celery background task:
	
    $ celery -A app.tasks worker --loglevel=info -f server.log &

    Celery is dependent on RabbitMq. RabbitMq is supposed to be setup and running before starting the celery app.

#### 4. Run the script:
    
    $ ./bin/server.py

## 2. Instructions to create and initialize the database.

No worries. I have used sqlalchemy which will take care of initializing Database for the first time. You don't have to do anything for it.

## 3. Assumptions I have made.

I have assumed server.py will be run on *nix environment.
I have assumed that clients mentioned in xml file will have access only by username and password and not by SSH KEY.

## 4. Requirements that I have not covered in my submission.

Support for Windows Client is not given. I have tested the client only and only on "Amazon Linux AMI release 2016.09". It is a blend of RHEL 6.x, RHEL 7 with a bleeding edge Fedora Kernel so I am hoping the client shell script should work on those too (THough I am not sure. Please try to test on Amazon Linux). I am not doiing any encryption/decryption explicitly for communication between client and server. I have used paramiko and as all communication is made through SSH, its already encrypted.

## 5. Issues I have faced while completing the assignment.

One of the major issue for me was collecting the statistics from all these different kind of operatings systems we have today. Giving support for all environments was a little time consuming thing so I used simple shell scripts. The client the I upload is the shell script now though in the improved version of this application I would really love to give "psutil" a try. psutil can support alot of different operating systems but the problem with using it is that you will need some way of comunicating back with the server. Incase of shell script, commucation was being done with help of ssh. "psutil" which will be a python script, cannot respond back over ssh. So for that we will need socket communucation over TCP. Server script will open a socket, will listen to incoming requests from clients and client will send the data back to it when the have it.



