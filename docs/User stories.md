# User stories
* wpaas admins should be able to segrate the customers for the following purposes
    * Billing - customer should be billed only for their own instances
    * ACcess control - customer should only be able to see, create/update in their own org space
    * Quota - Customer may have quotas to avoid flooding wpaas by single customer

* Every website should get a public IP
    Should we support named virtualhosting too? like multiple websites get same IPs, website name provided by
    customer will have a named virtual host added, also wpaas subdomain is also added. This may be provided
    feature options - customer may choose
    * To use one or just pool of IPs for them, which would be shared by their websites, 
    * To use new IPs for websites
    * To use complete named virtual hosting and no control in IP address for them

NOTE: This may be considered later stage as this would imcrease the complexity -

Question: What is the advantage of named virtual hosting vs ip based virtual hosting
    
* Every website should get a dns name from wpaas subdomain - like <route>.<website>.<customer org>.www.<wpaas domain>
    This name may be used for various purposes, like monitoring, testing, blue/green deployments etc.
    This name may be secured using basic auth.
## Providers - our direct customers those who (develop,) manage websites for their customers

* Providers (Our customers) should be able to use our apis/embed our JS library/url to their website to
    xxxxize this product, so that their users can come over to their website
    to do the stuffs (like oem vendors)
* Providers should be able to get the dashboard that may contain
    * wpaas instances that are in their org space
        * How those instances perform
            * Things like number of app instances, any relevant matrices (averages) like cpu, mem etc
        * Any traffic data including successful returns, errors, timeouts, average return time etc
        * Drill down support on traffic data  to analyze per page stats
* Providers should be able to group multiple websites together may be like a project level - so that they may 
get some of the matrics and billing details based out of group


## End users (those who create/load websites)
Here we talk about user stories for end users. End users are those who are actually loading the websites.
It may be website developers working for providers too

### New website loading  
* End users should be able to drag and drop website zip file to initialize or update the website

    Users should be able to create a running website by providing their website code zip file by drag
    and drop/load the file. If the loaded zip file doesnt contain all details (like website name etc) 
    to start a new wp instance,wpaas should analyze it and ask further questions (like a form loaded
    as next step in the wizard)
* End users should be able to start a blank WP instance by just fill a form  with basic details like
website name, admin password etc

    Once they get wp instance, they should be able to manage rest of the things to load 
    NOTE:  Do we need this facility? Check question in design.md

### Update website    
* End user should be able to opt for Version control of their website that include the code and any db changes
that made by each code version
* Each update should nternally make versions and exposed to the users
* Users should be able to provide a git url which contain the website code and in such case, any changes in the git
    branch (like master) of that repo should automatically trigger a website update 
* Rollback to previous version in a single click - This may be little tricky in case they do any schema changes due to any code change or
due to wp upgrade itself. But it may worth to investigate
* Various kind of updates for online updates
    USers may opt for online website update, in which case, we may support
        * Canary updates - start with one instance at a time, and let them test etc
        * Blue green update - create a new set of instances with different url, and let customers test and once 
         successfully tested, shift the traffic to production one and delete production set of instances
NOTE: We may or may not consider this feature as this is more suited for application deployment, websites may not need
this kind of CICD stuffs.   

### Auto scaling
* For those users who opted for autoscaling, wpaas should automatically scale out/in based out of the cpu/memory utilization
* Those who are not opted for autoscaling should be notified in case of resource utilization goes high
     
### Backup and restore
* Users should be able to opt for backup their website, in which case, the website should be backedup regularly
to S3 or something
* Users should be able to see backup details like how many backups are made and when etc, also They should be able
to download their backups for offline backups if they wish to
* Users should be able to restore their websites from their backups with single click

### Multi-region/HA support
* Optional Active/passive website support
* Optional active/active multi-region geo loadbalancing support 
Note: This may be considered in later point

### Other Features
* Profiles
    * Users may manage different profiles that contain different feature configs, which can be applied while
    starting a wpaas instance. For example, instead of configuring each wpaas instance with things like auto scaling
    configs, backup and restore, etc, one just apply a profile name while starting the instance.
    * There is one default profle that would be applied in case nothing is provided. 