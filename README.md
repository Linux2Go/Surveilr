# Getting Started #

Starting with an Ubuntu Oneiric box, install Riak:

## Riak setup ##

>     wget http://downloads.basho.com/riak/CURRENT/riak_1.0.2-1_ubuntu_11_amd64.deb
>     sudo dpkg -i riak_1.0.2-1_ubuntu_11_amd64.deb

You need to make a few changes to Riak's app.config.

>     sudo sed -e '/^ {riak_kv/ a {delete_mode, immediate},' \
>              -e 's/storage_backend, riak_kv_bitcask_backend/storage_backend, riak_kv_eleveldb_backend/' \
>              -e '/^ {riak_search/,+2 s/enabled, false/enabled, true/' -i.bak /etc/riak/app.config

Now we're ready to start Riak:

>     sudo /etc/init.d/riak start

## Other dependencies ##

`tools/setup_virtualenv.sh` will pull in all the necessary dependencies and should let you run the test suite:

>     tools/setup_virtualenv.sh
>     .venv/bin/python setup.py nosetests

## Running Surveilr ##

You can start Surveilr this easily:

>     paster serve surveilr/defaults.cfg
