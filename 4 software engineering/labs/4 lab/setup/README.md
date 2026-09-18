My app is divided into 2 part when it comes to the setup:
- the database is running on docker
- everything else is on wildfly.

You can find the setup for helios and for running the app locally on one docker container [here](https://github.com/worthant/interactive-graph-ui/blob/a13196e96ccde00697b9c7fa1db9fff15df5e262/README.md
)


## Database setup

First things first download Docker Desktop app from [official site](https://www.docker.com/products/docker-desktop/) if you don't have it

To the root folder of the project add **docker-compose.yml** file. You can use [my file](https://github.com/isaxel/web/blob/main/my_app3/docker-compose.yml) as an example.

In ports choose the port that your database will be running. In my setup it is **5432**.

```
ports:
      - "5432:5432"
```

Environment Variables:

```
      POSTGRES_PASSWORD: postgres
      POSTGRES_USER: postgres
      POSTGRES_DB: postgres
```

If you changed the port / name of database / password / username it is important you change it in **persistence.xml**

```angular2html
<property name="hibernate.connection.url" value="jdbc:postgresql://localhost:5432/postgres"/>
<property name="hibernate.connection.password" value="postgres"/>
<property name="hibernate.connection.username" value="postgres"/>
```

To run the database open Docker Desktop and  from the ../[project_root]/ directory run:

```bash
# First time: pulls the image and starts
docker-compose up -d

# Restart if you changed compose file:
docker-compose down
docker-compose up -d
```

To connect to database and test it run:
```
psql -h localhost -p 5432 -U postgres -d postgres
```

## Wildfly

### 1\ Download wildfly

I used the wildfly-preview-26.1.3.Final version. You can download it on [official site](https://www.wildfly.org/downloads/). Keep in mind that your
version of wildfly should be compatible with the version of JavaEE you are using (for jakarta it is 22+ version of widlfly;
for javax it is 21 and older versions of wildfly). Also keep in mind that it should be the **preview** version specifically.

Download zip archive and unpack it to the folder of your choosing.

### 2\ Change the standalone.xml file

Go to ``../[wildfly-root]/standalone/configuration/`` and open **standalone.xml** with a text reading / changing app.


You can also replace it with my [standalone.xml](standalone.xml) file from this repository and proceed to the 3 point of this instruction.

#### 2\1 Portbase

At the end of the file change the portbase on which the app wil be running. I am using the **32318** port so the changes will be

```angular2html
<socket-binding name="ajp" port="${jboss.ajp.port:32319}"/>
<socket-binding name="http" port="${jboss.http.port:32318}"/>
<socket-binding name="https" port="${jboss.https.port:32320}"/>
<socket-binding name="management-http" interface="management" port="${jboss.management.http.port:32321}"/>
<socket-binding name="management-https" interface="management" port="${jboss.management.https.port:32322}"/>
```

#### 2\2 Database

Change the default database to postgresql

```angular2html
<datasource jndi-name="java:jboss/datasources/ExampleDS">
    <connection-url>jdbc:postgresql://localhost:5432/postgres</connection-url>
    <driver>postgresql</driver>
    <security>
        <user-name>postgres</user-name>
        <password>postgres</password>
    </security>
</datasource>
```

Keep in mind
- PostgreSQL must be running
- Database name: postgres
- User: postgres
- Password: postgres
- Port: 5432


#### 2\3 HTTPS listener and redirecting HTTP to HTTPS

```angular2html
<server name="default-server">
    <http-listener name="default" socket-binding="http" redirect-socket="https" enable-http2="true"/>
    <https-listener name="https" socket-binding="https" ssl-context="applicationSSC" enable-http2="true"/>
    <host name="default-host" alias="localhost">
        <location name="/" handler="welcome-content"/>
        <http-invoker http-authentication-factory="application-http-authentication"/>
    </host>
</server>
```

#### 2\4 All interfaces listening

```angular2html
<interfaces>
    <interface name="management">
        <inet-address value="${jboss.bind.address.management:127.0.0.1}"/>
    </interface>
    <interface name="public">
        <any-address/>
    </interface>
</interfaces>
```

#### 2\5 Security manager

```angular2html
<subsystem xmlns="urn:jboss:domain:security-manager:1.0">
    <deployment-permissions>
        <maximum-set>
            <permission class="java.security.AllPermission"/>
        </maximum-set>
    </deployment-permissions>
</subsystem>
```

#### 2\6 Logger

add
```angular2html
<logger category="org.jboss.as.config">
    <level name="DEBUG"/>
</logger>
```

#### 2\7 JDBC-driver PostgreSQL in WildFly

Change the driver name to PostgreSQL.

``` 
<driver name="postgresql" module="org.postgresql">
```

### 3\ JDBC-driver PostgreSQL

Wildfly doesn't have PostgreSQL-drive by default so we have to add it manually. 


You can also use my files [module.xml](module.xml) and [postgresql-42.7.3.jar](postgresql-42.7.3.jar) from this repository in the following instructions

#### 3\1 Download driver

Download driver from [official site](https://jdbc.postgresql.org/download/), for example
``` 
postgresql-42.7.1.jar
```

#### 3\2 Make directory

```bash
..../[wildfly-root]/modules/system/layers/base/org/postgresql/main
```

#### 3\3 Put the driver file there

#### 3\4 Make module.xml in this directory

```angular2html
<?xml version="1.0" encoding="UTF-8"?>
<module xmlns="urn:jboss:module:1.0" name="org.postgresql">
    <resources>
        <resource-root path="postgresql-42.7.3.jar"/>
    </resources>
    <dependencies>
        <module name="javax.api"/>
        <module name="javax.transaction.api"/>
    </dependencies>
</module>
```

## Running

for the database from the ``../[project_root]/`` directory run
```bash
docker-compose up --d
```

for the app from the ``../[wildfly-root]/`` directory run
```bash
./bin/standalone.bat
```

So the final app can be launched at 

```
http://localhost:32318/my_app3
```

where **32318** is the portbase, **my_app3** - name of your *.war archive of the app

Congratulations, now you can run your app locally and test it on your machine!!