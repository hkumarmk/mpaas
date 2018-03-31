# High level design

# API Design
## Customer api
To register and manage customers. Each customer will have one org space with the name as customer id, in which  
at least one project under which all the resources are managed.

### Add/Register customer
Customer may be registered with details like customer name, email id and credentials added - we may integrate with
google/github/linkedin sso auth. 

POST to /customers api endpoint with below details
* Customer name
* email id
* username (it may be email id too)
* password (or SSO integrated by providers like google, github, linkedin)

On creating customer, we will create below additional details
* customer id - a unique id that identify the customer - we may create it by taking first 3 letters (or more) from
customer name - this id may be used in various other data/objects within the system.
* status - status id like free, paid, suspended, etc
* Any payment identifier or something that may be received from payment/billing integration system
* Any payment status id from payment integration system -

This would call /projects api to create default project (named default)

### Manage or update the customer
PUT to /customers/<customer id> with appropriate data to be updated

### Get all customers data
GET to /customers/ 

### Get specific customers data
GET to /customers/<cid>

### Delete customer
This would cause all customer data deleted - it would do a DELETE call to /projects to delete all projects for the customer
DELETE to /customers/<cid>

## Projects api
The projects api is used to manage projects within an org space (under customer). Each customer will have at least one
project in which the resources like wpaas instances are managed. There is a default project is created on customer
registration. Each wpaas instances will be created under a specific project. Users may have access controlled based
on the projects.

### Create project
POST to /projects with below data
* Name: Name of the project
* Description
* cid - customer id in which the project is created - user should have access to the customer org to successfully
create a project
* Any quota configs

## Update a project
PUT to /projects/<cid>/<project name> or /proects with cid and project name and other data to be updated

### Get project details
GET to /projects with cid and optionally proect name

### Delete project
DELETE to /projects/<cid>/<project name>

## Users api
Each customers may have multiple users. Once a customer is registered, he may perform user management using the email id
and credentials that is provided on registering the customer. And it is highly recommented to keep that credentials
secured and create other users with various access to perform day-to-day operations.

### Add users
POST to /users with below details
* name
* CID - customer id
* password
* email id
* projects: list of projects this user has access
* enabled: True/False

It automatically add below details 
* Api key - this may get updated in certain duration, users may have to get updated key 

### Update users
PUT to /users/cid with cid and other details that need to be updated

### Get users
GET to /users/cid to get all user details, if provide name=username, specific user etc

### Delete users
DELETE to /users/cid/username

## wpaas api
This manage wpaas instances - a wpaas instance has:
* One ore more wordpress instances
* Database service
* A public IP assigned (In future we may support named virtualhosting too to reduce number public IPs)
* A dns name i.e www.abc.com - this is provided by customer, and managed externally by customer
* A wpaas subdomain dns name like <route>.<website name>.<customer org>.www.<wpaas domain> where route may be optional string
that may point to version or for any other purposes

### Add wpaas instance
POST to /wpaas/cid/project_name/ with below details
```
name: website name
code: s3 bucket name or git url where we kept the code
num_instances: number of wp instances\
admin_password: pass
features:
  autoscale: true/false
  blah: blah
```
while adding wpaas instance, there are series of operations happen.
* Update the datastore with new wpaas instance something like /wpaas/cid/project_name which have keys as below
    * expected_num_instances
    * num_instances
    * code_url
    * features/autoscale
    * etc etc
* converger would converge the system to make sure the wpaas instances available that match expected numbers
* Converger also monitor the system all the time and converge any gaps it found

### Update wpaas instance
PUT to /wpaas/cid/project_name/wpaas_name with appropriate configs that to be changed

It may cause converger to converge the system to match actual state to the expected state

### Get wpaas instances
GET to /wpaas/cicd/project_name - with appropriate filters

### Delete wpaas instances
DELETE to /wpaas/cicd/project_name/wpaas_name - 


### QUESTIONS:
* What are the reasons to provide wp access to the customers?
    We need to investigate on what all reasons a customer need wp admin access. If the actions they would be performing
    in admin ui is not much, why can't we provide them in our interface,
    I think lot of them would be handled within the website code itself.
    The advantage of having our customer uses our own interface is that complete control over wp instances, also
    we can easily perform various extra features like autoversioning the websites, rollback to previous versions
    in single click (including db changes) etc.