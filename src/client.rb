#
# Chef Client Config File
#  Basic config  
#
log_level          :warn
log_location       "/var/log/chef/client.log"
ssl_verify_mode    :verify_none
chef_server_url    "http://chef:4000"

validation_client_name "chef-validator"
validation_key      	 "/etc/chef/validation.pem"
client_key          	 "/etc/chef/client.pem"

cache_options({ :path => "/var/cache/chef/checksums", :skip_expires => true})

signing_ca_user "chef"

file_cache_path    "/var/chef/cache"
pid_file           "/var/run/chef/client.pid"

Mixlib::Log::Formatter.show_time = true

 

