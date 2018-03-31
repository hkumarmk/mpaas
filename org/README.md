# Org microservice

This microservice will manage org details under each customer. Each customer may have multiple orgs managed,
depending on the requirements.

Orgs provide a completely independent place to manage the apps(e.g wpaas) with complete isolation from
other orgs even within the same customer. They are managed and billed separately.

Each org will have at least one space that provide logical separation to host different projects. 

# Install it
* Setup virtualenv
  * Install virtualenv
  * Run command "virtualenv $HOME/venv"
  * activate that venv by running command "source $HOME/venv/bin/activate"
  * run command "python setup.py install" from within mpaas directory

# Run it - this is for testing only

NOTE: For test mode, it use sqlite db. For actual usecases, we should use either mysql or postgres.

Change to "org" directory and run "python main.py". This would run the app in a debug, test mode and would be listen
on port 5001, on localhost. If you want to change listen address or listen port, you may export the variables
ORG_APP_LISTEN_ADDR and ORG_APP_LISTEN_PORT.

```
(.venv) root@ubuntu-xenial:/vagrant/mpaas/customer# python app.py 
 * Running on http://127.0.0.1:5001/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 170-181-683
```
# Use it
One may use curl to use it

* Add customer
    ```markdown
    # curl -X POST  -H "Content-Type:application/json" -d '{"apps": "wordpress"}' http://localhost:5000/customers/harish1
    {
      "Customer": [
        {
          "apps": [
            "wordpress"
          ], 
          "id": 5, 
          "name": "harish1"
        }
      ]
    }
    
    ```
* Show all customers
    ```markdown
    # curl  http://localhost:5000/customers
    {
      "Customer": [
        {
          "apps": [
            "wordpress"
          ], 
          "id": 1, 
          "name": "harish"
        }, 
        {
          "apps": [
            "wordpress"
          ], 
          "id": 2, 
          "name": "harish1"
        }
      ]
    }
    ```
* Show specific customer
    ```markdown
    # curl  http://localhost:5000/customers/harish
    {
      "Customer": [
        {
          "apps": [
            "wordpress"
          ], 
          "id": 4, 
          "name": "harish"
        }
      ]
    }
    ```
