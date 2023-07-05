FROM ubuntu:18.04

RUN apt-get update && \
      apt-get -y install sudo

# fixes prompts during apt installations
RUN echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections
RUN sudo apt-get install -y -q
RUN DEBIAN_FRONTEND=noninteractive sudo apt-get -y install keyboard-configuration

RUN sudo apt-get -y update && sudo apt-get -y install software-properties-common git

RUN mkdir -p /opt/klaxalk/git && cd /opt/klaxalk/git && git clone https://github.com/klaxalk/linux-setup --depth 1

RUN sudo apt-get -y install python-matplotlib python3-pip python3-tk python-pmw python-pip python-mpltoolkits.basemap python3-mpltoolkits.basemap python-scipy python-ephem

CMD ["bash"]
