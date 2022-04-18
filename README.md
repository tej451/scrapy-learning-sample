## Running the application in local:

Prerequisites (Installation instructions are added below):
1. Python 2.7 
2. Aquarium - https://github.com/TeamHG-Memex/aquarium
3. RabbitMQ 
4. MongoDB
5. scrapyd - https://scrapyd.readthedocs.io/en/latest/index.html#


After cloning the application in local please run "python setup.py install" from the project root directory so that all the project dependencies will be added to python path.
* Included the Gradle integration approach from - https://github.com/linkedin/pygradle for future updates
* Needs a pre-setup of artifactory of Python packages with enhanced ivy metadata - Can be acheived by https://github.com/linkedin/pygradle/blob/master/docs/pivy-importer.md
* For now limiting the scope to setup.py for simplicity

Update the "settings.py" with the server adresses of aquarium, RabbitMQ, MongoDB

1. SPLASH_URL = 'http://{aquarium-host}:8050/'
2. RABBITMQ_CONNECTION_PARAMETERS = 'amqp://{rabbitmq-user}:{rabbitmq-password}@{rabbit-mq-host}:5672/'
3. MONGO_URI = "mongodb://{mongodb-user}:{mongodb-password}@{mongo-db-host}:27017/{db-name}"	



## Deploying

### Deploying to 'scrapyd'

1. Update the "scrapy.cfg" with the scrapyd server adresses 
    [deploy]
     url = http://{scrapyd-server-host}:6800/
2. Run "scrapyd-deploy.py" from project root directory  	 

@ToDo: Create a Jenkins Build & Deploy job for this step
### Deploying to 'ScrapingHub':

##### Create ScrapingHub account and go to the root path of cloned application in local and run the following
* $ pip install shub
* $ shub login
* API key: <api-key>   # enter the api-key from scraping-hub account eg: cg3c784b5c3c4d2a8g3fb4c52f3c1081
* $ shub deploy 289890
 
##### Sample output:
* C:\Users\Ktejkum\eclipse-workspace\bmc>shub deploy 236820
* Packing version 28d34ec-master
* Deploying to Scrapy Cloud project "236820"
* Run your spiders at: https://app.scrapinghub.com/p/236820/
* {"version": "28d34ec-master", "status": "ok", "project": 236820, "spiders": 5}

Note: if you have any dependent modules then please create a 'requirements.txt' with all needed versions of modules in the project root path and refer it in 'scrapinghub.yml'
eg: requirements_file: requirements.txt

2. Login to ScrapingHub account and run the spiders by passing arguments brand,division,category etc and check the logs etc
https://app.scrapinghub.com/account/login/

## Running 
Run the crawler in two ways in local
1. From "SpiderRunner.py" by passing the "spider_params" eg: {'brand' : 'GAP', 'division' :'men', 'category':'jeans'}
2. From "main.py" by passing the parameters eg: ['-a' 'brand=gap', , '-a' 'division=men', '-a' 'category=Innovation Studio']

Run the crawler from scrapyd
* Run a spider with
* $curl http://{scrapyd-server-host}:6800/schedule.json -d project={project-name} -d spider={spider-name} -d brand={brand-name} -d division={division-name} -d category={category-name}
* Eg: $curl http://localhost:6800/schedule.json -d project=bring-me-to-cart -d spider=BaseSpider -d brand='GAP' -d division='Men' -d category='Innovation Studio'
* To crawl entire brand please use only 'brand' parameter 
* Eg: $curl http://localhost:6800/schedule.json -d project=bring-me-to-cart -d spider=BaseSpider -d brand='GAP'
* To crawl a brand specific division please use only 'brand' and 'division' parameters 
* Eg: $curl http://localhost:6800/schedule.json -d project=bring-me-to-cart -d spider=BaseSpider -d brand='GAP' -d division='Men'
##### To run all brands
* Use "bmc_runner.sh" found on project root directory (GAP, BR, ON, ATHLETA)
* Will spins brand specific jobs here.

## Monitor Jobs: 
Can monitor running jobs and logs from Scrapyd web-client : http://{scrapyd-server-host}:6800/jobs

To cancel a job $curl http://{scrapyd-server-host}/cancel.json -d project={project-name}  -d job={job-id}


## Improvements / Next Steps:
* Pause/resume feature
* Distribution crawling mode (seperate the 'crawler' and 'scraper' spiders and run on multiple "scrayd" servers)
* UI to run and schedule
* Use "python-scrapyd-api" (http://python-scrapyd-api.readthedocs.io/en/latest/) for better handling of jobs.

## Install Prerequisites: (Instructions for Ubuntu 16.04)
### 1. Install Docker:

* curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
*	sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
*	sudo apt-get update
*	apt-cache policy docker-ce
*	sudo apt-get install -y docker-ce
*	sudo systemctl status docker

The output should be similar to the following, showing that the service is active and running:

Output
* docker.service - Docker Application Container Engine
   Loaded: loaded (/lib/systemd/system/docker.service; enabled; vendor preset: enabled)
   Active: active (running) since Sun 2016-05-01 06:53:52 CDT; 1 weeks 3 days ago
     Docs: https://docs.docker.com
 Main PID: 749 (docker)

### 2. Install pip
 
 * sudo apt-get install python-pip
 
### 3. Install Docker-Compose
 
 *	sudo curl -o /usr/local/bin/docker-compose -L "https://github.com/docker/compose/releases/download/1.15.0/docker-compose-$(uname -s)-$(uname -m)"
 *	sudo chmod +x /usr/local/bin/docker-compose
 *	docker-compose -v
 ##### Output :
 * docker-compose version 1.15.0, build e12f3b9

### 4. Install Aquarium
 
 * pip install cookiecutter
 * cookiecutter gh:TeamHG-Memex/aquarium
  (With all default options it'll create an aquarium folder in the current path. Go to this folder and start the Splash cluster:
   cd ./aquarium )
 * docker-compose up

### 5. Install RabbitMq

#### Step 1 – Install Erlang

* $ wget https://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb
* $ sudo dpkg -i erlang-solutions_1.0_all.deb
* $ sudo apt-get update
* $ sudo apt-get install erlang erlang-nox

#### Step 2 – Install RabbitMQ Server
* $ echo 'deb http://www.rabbitmq.com/debian/ testing main' | sudo tee /etc/apt/sources.list.d/rabbitmq.list
* $ wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | sudo apt-key add -
* $ sudo apt-get update
* $ sudo apt-get install rabbitmq-server

#### Step 3 – Manage RabbitMQ Service
* $ sudo systemctl enable rabbitmq-server
* $ sudo systemctl start rabbitmq-server

#### Step 4 – Create Admin User in RabbitMQ

* $ sudo rabbitmqctl add_user admin admin 
* $ sudo rabbitmqctl set_user_tags admin administrator
* $ sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
#### Step 5 – Setup RabbitMQ Web Management Console
* $ sudo rabbitmq-plugins enable rabbitmq_management



