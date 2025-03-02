This code can be put on a pi zero connected to the enviro+ board. It passes all the data to a local mqtt broker.

As of 2nd March 2025, I haven't got this to run reliably - the pi goes dark on the network after some time.

To set everything up:
1) Flash the pi zero with network credentials and ssh into it

```ssh christian@192.168.7.231```

2) Install Enviro+ Python Library (allowing install.sh to creat a new venv)

```git clone https://github.com/pimoroni/enviroplus-python```
```cd enviroplus-python```
```./install.sh```

3) Clone this repo

```cd ..```
```git clone https://github.com/ChristianFieldhouse/enviroplus_mqtt_logging.git```

4) Reboot the pi zero, wait a minute, and ssh back into the pi zero

```sudo reboot```

5) Take a look at the .service file. Make sure the User and ExecStart have the right user names. You'll also want to run the ExecStart to check it runs.

```cat enviroplus_logging.service```

6) make a symbolic link to the .service file, enable, and start it

