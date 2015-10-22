# Making sure ssh user@localhost works
mkdir -p ~/.ssh
ssh-keyscan -t rsa,dsa localhost >> ~/.ssh/known_hosts
echo -e "\n\n\n" | ssh-keygen -t rsa -N ""
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
