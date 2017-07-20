# Managed PAAS (MPAAS)
Idea is to develop a managed platform system that support deploying end user services/application within it.

To start with we would be supporting wordpress - all OS instances, Support services would be managed by the provider
and Wordpress is managed by the user.

# What is there at this moment
Just start working on it. Currently there is an ansible code to configure various mysql databases provided on specific
db nodes and start wordpress with apache containers on web nodes.

# Features

# TODO 

## Short term
* Use php-fpm wordpress containers with nginx containers in front - so that php-fpm handle php, and nginx handle static
pages
* Write rest api to do at least following operations
    * Add/remove/update nodes on various types (db nodes, web nodes, etc) - while adding a node, the node is configured
    to launch the service. i.e db node has mysql running and ready to create db on it, where install docker on web node
    and ready to start docker containers
    * Add/remove/update services
        * Databases (customeer databases)
        * php-fpm + wordpress, nginx/apache
        * Shares
        * Monitoring
* Use php-fpm + wordpress and nginx as web. Currently use worpress + apache container
* Add Redundant systems
    * Database replication
    * Shared storage (NFS/Gluster/ceph)
    * Load balancers (haproxy)
    * HA for load balancers
* Other supporting systems
    * Reverse proxy for page caching
    * Redis/Memcache for db caching
* Monitoring
    * System monitoring
    * Options for wordpress monitoring
    * Log aggregation and analysis
* db replication - master-master/master-slave
* Basic security
* Automation for wordpress initial setup - i.e sitename, user creds etc (may be it make sense to have user )
## Long term
* Authentication and authorization
* SSO ?
* Apis for below ops
    * Add/Remove/update cloud endpoints (may be..) 
    * Add/remove/update datacenters - virtual datacenters may be
* Security
