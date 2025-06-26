# ![HayStacker48](https://github.com/user-attachments/assets/928ff259-e1b2-4e8a-a748-22540dbb1f68) HayStacker
🏷️ Making custom tracking _tags_ easy

## What is HayStacker? 🪡
HayStacker is a GUI application & framework for all platforms that lets _you_ create and track tags via Apple's FindMy network.
Tags don't need to connect to a network and can be tracked on any system; Windows, Linux, and Mac!
The goal is to allow the everyday person to create tracking tags to track everyday objects (Backpacks, Bicycles, Keys, etc), and to provide a simple, cross-platform GUI interface that makes this accessable to anyone.

![haystacker](https://github.com/user-attachments/assets/f718a8f9-c6a8-4281-bd3d-0817d9db79b8)  
<br/>

## How is this possible? 💾

Thanks to the hard work and research by the folks over at Seemoo Lab, the basis for querying apple servers was established:
- https://github.com/seemoo-lab/openhaystack

Next, credit is given to Dadoum for the anisette-v3-server project and Biemster for the FindMy project. These two established the grounds for moving OpenHayStack's frameworks away from being MacOS-only:
- https://github.com/Dadoum/anisette-v3-server
- https://github.com/biemster/FindMy

This project finishes the job off by porting all that hard work to cross-platform compatable Python, wrapping it all up in a nice little package, and developing a GUI. And here you are!  
<br/>

## How can I install it? 🖥️

In an effort to be modular and easy to update, this project doesn't need to be compiled.

- 🌟 Simply download the code, extract (if necessary), and double-click the launch script for your platform

Windows:
```
winLaunch.bat
```
  
MacOS / Linux:
```
macLinuxLaunch.sh
```
<br/>

## How-to Guide 🧐

### Flashing an ESP32 Board
- Choose a tag to deploy, or create a new one using the `+` button
  - If creating a new tag, enter a name when the dialog opens
  - ![image](https://github.com/user-attachments/assets/6e3c4109-f441-4c3e-8d74-9fa5cd9d50ef)
- Plug in your ESP32
- Click `Deploy` next to your desired tag
- Choose your COM port to deploy to
  - ![image](https://github.com/user-attachments/assets/3ba92a84-46b9-4610-b6ce-bab5fe2f132f)
  - If the COM port does not appear, make sure the proper serial drivers for your board are installed and your cord can transmit data
- Watch as the software deploys!

### Locating tags
- Click the `⟳` or `Login to Apple` button in the top-right
- Follow the log-in instructions. Your apple account is necessary to pull data from Apple servers.
  - ![image](https://github.com/user-attachments/assets/ec09e736-de21-4e0c-819e-809265dacef2)
  - ⚠️ If you have no Apple devices associated with your Apple ID, you may use SMS authentication. Keep in mind that SMS authentication is often faulty and Apple will randomly block SMS authentication requests
- Your tags, if pinging and near an Apple device, will appear on the map.
