theory [here](https://github.com/web-labs/Web-Lab-3/blob/main/theory.md) and [here](https://github.com/BrightGir/itmo_labs/blob/main/web_labs/lab3/questions/)

#### my instruction for setting the app locally [here](/setup/README.md)

### Running locally

For the database from the ``../[project_root]/`` directory run
```bash
docker-compose up --d
```

For the app from the ``../[wildfly-root]/`` directory run
```bash
./bin/standalone.bat
```

So the final app can be launched at 
```
http://localhost:32318/my_app3
```

where **32318** is the portbase, **my_app3** - name of your *.war archive of the app

Congratulations, now you can run your app locally and test it on your machine!!