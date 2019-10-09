# docker integration for growing automation project

create env: `cp env-distrib .env`

Fill in the missing spots and save .env file.

#### Build docker image

`docker-compose build`

#### Deploy a container

`docker-compose up`

#### On first run

If the container is run for the first time the database must be initialised
using the following commands:

```
Open new terminal and enter the buildet container terminal:
$ docker exec -it event_rules_storage_api /bin/ash     
  /container terminal commands... /
  $ flask db init
  $ flask db migrate
  $ flask db upgrade

  $ exit
```

