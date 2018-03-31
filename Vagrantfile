# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|

  default_flavor = 'small'
  default_image = 'trusty'

  # allow users to set their own environment
  # which effect the hiera hierarchy and the
  # cloud file that is used
  cluster_size = ENV['cluster_size'] || 3
  image = ENV['image']||"ubuntu/xenial64"
  cpu = ENV['cpu'] || 1
  ram = ENV['ram'] || 1024
  environment = ENV['env'] || 'vagrant-vbox'
  layout = ENV['layout'] || 'full'
  map = ENV['map'] || environment

  config.vm.provider :virtualbox do |vb, override|
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

  last_octet = 41

#  machines = {}
#  (1..cluster_size).to_a.each do |idx|
#    machines["node#{idx}"] = info
#  end

  (1..cluster_size).to_a.each do |idx|

    config.vm.define("node#{idx}") do |config|

      config.vm.provider :virtualbox do |vb, override|
        override.vm.box = image
        vb.memory = ram
        vb.cpus = cpu
      end
      config.vm.synced_folder "../", "/vagrant"
      config.vm.host_name = "node#{idx}.domain.name"
     # config.vm.network :private_network, type: "dhcp"
      config.vm.provision 'shell', :inline => <<-SHELL
      apt-get install -y apt-transport-https curl
      curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
      echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list
      apt-get update
      # Install docker if you don't have it already.
      apt-get install -y docker.io kubelet kubeadm kubectl kubernetes-cni
      SHELL
    end
  end
end
