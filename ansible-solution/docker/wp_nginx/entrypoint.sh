#!/bin/bash

cat <<EOF > /etc/nginx/conf.d/wordpress.conf
server {
    listen ${WEB_PORT};
    server_name ${SERVER_NAME};
 
    root /var/www/html;
    index index.php;
 
    access_log /var/log/nginx/${SERVER_NAME}-access.log;
    error_log /var/log/nginx/${SERVER_NAME}-error.log;
 
    location / {
        try_files \$uri \$uri/ /index.php?\$args;
    }
 
    location ~ \.php\$ {
        try_files \$uri =404;
        fastcgi_split_path_info ^(.+\.php)(/.+)\$;
        fastcgi_pass ${BACKEND_SERVER}:${BACKEND_PORT};
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
        fastcgi_param PATH_INFO \$fastcgi_path_info;
    }
}
EOF
nginx -g "daemon off;"

