HOW TO REPRODUCE MY TEST SETUP

1)	Get a rPi4 64 bit and set it up with a regular headless Raspberry PI OS (64 bit). Basically follow all the steps here: https://github.com/kercre123/wire-prod-pod 
    in the paragraph “Set up wire-pod”, step 1 to 5.
2)	When you are logged in on your RPI, clone my gir repositories for wire-pod and vector sdk:
	git clone https://github.com/fforchino/vector-python-sdk.git
	git clone https://github.com/fforchino/wire-pod.git
3)  Also download the media files needed to run the example, they're just a bunch of mp3s:
	wget http://www.borgomasino.net/vector/audiofiles.tar
    tar xvf audiofiles.tar
4)  Now build wire-pod:
    cd /home/pi/wire-pod
	sudo ./setup.sh
	And do the full setup
	I am currently using Leopard as tts engine, you can try out vosk but it's not yet optimal, their standard English language model is a bit too big and this 
	slows down the voice recognition. Anyway its performanece is not too bad.
	I run the server on escapepod.local, port 8080 for web server
5)  Setup the SDK:
    cd /home/pi/vector-python-sdk
	./configure.py
6)  Test that the sdk is working
    cd 	/home/pi/vector-python-sdk/wire-pod
	./say.py ""
	Vector shoud say some random sentence
7)  Now build chipper 
    cd /home/pi/wire-pod/chipper
	sudo ./start.sh
    This should build it and start it
8)  You can now test the whole combination is working:
    "Hey Vector"
	"Say something"
	If the sentence is recognized, it should trigger a custom intent that invokes the /home/pi/vector-python-sdk/wire-pod/say.py script
	The key thing to make it work is to note that wire-pod normally runs as root, while the sdk needs to be run by the pi user
	That's why I don't call the .py scripts directly but through a runCmd.sh script that uses the "runuser" command to allow root to launch the .py
	scripts as the user pi.

About Vector side
Initially I had my sdk and Vector still bound to Anki server and certificates. Nothing was working for me until I did the following:
1. Create an account at DDL (same email and pwd of my old Anki account)
2. (Reset user data on Vector). Reboot in recovery mode, open the companion app and connect to Vector (remember to double press the pairing button when the app is searching for him over BT) 
3. This downloaded on Vector the 2.0 OTA image
4. I checked that Vector could pair and work with the companion app. 
5. Perfect. At this point all the usual apps (like Vector Explorer) started working again
6. I ran the Python SDK on Windows and was also able to communicate with Vector
7. I followed the procedure at https://github.com/kercre123/wire-prod-pod par. "Set up the bot" do download WireOs Escape pod OTA
8. Vector now connects with my rPi, I have full control on the back end and I can write custom commands implementations

