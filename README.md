# seans-tabletop-audio

A FoundryVTT repackaging of some of the Creative Commons material from Tabletop Audio

## Setup in FoundryVTT

- Clone the seans-tabletop-audio repo to your modules folder.

      cd FoundryVTT/Data/modules
      git clone https://github.com/seansbox/seans-tabletop-audio.git

- Add Seans's Tabletop Audio module to your world.

- Find the Tabletop Audio adventure pack and click it.

- Import the module and your Tabletop Audio playlist will appear!

## Note About GitHub on Linux

- Generate an SSH key for your email.

      git config --global user.email "seansbox@gmail.com"
      ssh-keygen -t rsa -b 4096 -C "seansbox@gmail.com"
      cat ~/.ssh/id_rsa.pub
      git remote set-url origin git@github.com:seansbox/seans-tabletop-audio.git

- Paste the key to https://github.com/settings/keys.
