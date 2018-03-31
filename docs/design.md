# High level design
## Customers
Each customer would be registered with an email id that would have admin access to all org created under
that customer. This id/email may only be used to manage orgs, and users. Each org have set of users
to manage those orgs
## Orgs
Each customer would have one or more orgs created. Orgs provide a completely independent place to manage
the apps(e.g wpaas) with complete isolation fromm other orgs even within the same customer. All app instances
are deployed under one org, so every customer will have at least one (Default) org.

Customers may opt to create seperate orgs because of reasons below
* They need completely independent app instances (wpaas instances), which may host different organization
or team apps
* They may need to get them indepdendently managed and get independent billing

## Space
Space is a logical separation within an org because of may be 1. to implement quota for individual team apps
(wpaas instances), or 2. There may be different teams working on different wpaas instances, and thus would
need to provide access control to only those systems which individual team working on.

Each org must have at least one space under which the apps would be deployed and managed.

## WPAAS instance
Wpaas instance is set of systems including db, wordpress instance[s] serving single wordpress website.
There would be multiple wordpress/db instances would be runnign withn single wpaas instance to provide
enough redundency and failsafe. 
 

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

## org api
The org api is used to manage projects within an org space (under customer). Each customer will have at least one
org (and space) in which the resources like wpaas instances are managed. There is a default org is created on customer
registration. Each wpaas instances will be created within an org. Each org is completely independent and 
billed separately.

### Create org
POST to /orgs with below data
* Name: Name of the org
* Description
* cid - customer id in which the project is created - user should have access to the customer org to successfully
create a project
* Any quota configs
* spaces - list of spaces 
## Update a org
PUT to /orgs/<cid>/<org name> or /proects with cid and org name and other data to be updated

### Get org details
GET to /orgs with cid and optionally org name

### Delete org
DELETE to /orgs/<cid>/<org name>

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