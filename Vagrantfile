# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.provider "docker" do |d|
    d.has_ssh = true
    d.image = "pr3sto/repullet:v2"
    d.ports = ["20000:80"]
    d.volumes=["/root/Documents/repullet/config.py:/var/www/repulletapp/config.py"]
    config.vm.provision "shell", inline: <<-EOC
      sudo /etc/init.d/apache2 start
      sudo a2ensite rePullet.conf
      sudo /etc/init.d/apache2 reload
      sudo LC_ALL="en_US.UTF-8" /etc/init.d/mongodb start
    EOC
  end
end

