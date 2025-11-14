sudo apt-get update && sudo apt-get install -y acl
sudo setfacl -m u:www-data:x /home/azureuser
sudo setfacl -m u:www-data:rx /home/azureuser/lengkeng-api
sudo setfacl -Rm u:www-data:rx /home/azureuser/lengkeng-api/storage
sudo -u www-data ls /home/azureuser/lengkeng-api/storage | head -n 5
sudo nginx -s reload