#!/bin/bash
sudo yum update -y
sudo yum install httpd -y
sudo yum install mysql -y
sudo systemctl enable httpd
sudo systemctl start httpd
echo "<h1>The hostname of my server is $(hostname -f)</h1>" > /var/www/html/index.html