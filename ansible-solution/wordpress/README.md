# Wordpress microservice

This microservice will manage customer wordpress instances.

It use customer microservice to get the details of customers and users may use customer microservice to determine if a customer
has wordpress platform available.


# Install it
* Setup virtualenv
  * Install virtualenv
  * Run command "virtualenv $HOME/venv"
  * activate that venv by running command "source $HOME/venv/bin/activate"
  * run command "python setup.py install" from within mpaas directory

# Run it - this is for testing only

NOTE: For test mode, it use sqlite db. For actual usecases, we should use either mysql or postgres.

Change to "customer" directory and run "python app.py". This would run the app in a debug, test mode and would be listen
on port 5000, on localhost. If you want to change listen address or listen port, you may export the variables
CUSTOMER_APP_LISTEN_ADDR and CUSTOMER_APP_LISTEN_PORT.

```
(.venv) root@ubuntu-xenial:/vagrant/mpaas/customer# python app.py 
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
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
