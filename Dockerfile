# Using tf-gpu image as base for Deep RL applications of rai-python
FROM tensorflow/tensorflow:latest-gpu
# Digest:sha256:37c7db66cc96481ac1ec43af2856ef65d3e664fd7f5df6b5e54855149f7f8594

# TODO mount volume for scratch?

# install git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

# install apt utils
RUN apt-get install -y apt-utils

# for compatibility with makefiles, install sudo
RUN apt-get install sudo

# install additional shared libs needed for rai
RUN apt-get install -y libceres-dev
RUN apt-get install -y libatlas-base-dev
RUN apt-get install -y libtbb-dev

ENV HOME /root
RUN mkdir $HOME/git
RUN mkdir $HOME/opt
RUN echo $HOME/git
WORKDIR $HOME/git

# install PHYSX
RUN git clone https://github.com/NVIDIAGameWorks/PhysX.git && \
    cd PhysX && \
    git checkout 3.4 && \
    cd PhysX_3.4/Source/compiler/linux64 && \
    make release
RUN mkdir -p $HOME/opt/physx3.4/lib && \
    mkdir -p $HOME/opt/physx3.4/include/physx && \
    cd $HOME/git/PhysX && \
    cp PhysX_3.4/Bin/linux64/* $HOME/opt/physx3.4/lib && \
    cp PhysX_3.4/Lib/linux64/* $HOME/opt/physx3.4/lib &&\
    cp PxShared/bin/linux64/* $HOME/opt/physx3.4/lib &&\
    cp -R PhysX_3.4/Include/* $HOME/opt/physx3.4/include/physx &&\
    cp -R PxShared/include/* $HOME/opt/physx3.4/include/physx && \
    rm -Rf $HOME/git/PhysX
ENV LD_LIBRARY_PATH "$LD_LIBRARY_PATH:$HOME/opt/physx3.4/lib"

# copy rai-python
RUN mkdir -p $HOME/git/rai-python
ADD . $HOME/git/rai-python/
RUN ls -l $HOME/git/rai-python/
RUN du -hs $HOME/git/rai-python/

# install rai-python
RUN cd rai-python && \
    make cleanAll
RUN cd rai-python && \
    yes | make installUbuntuAll
RUN cd rai-python && \
    make

# install pytest
RUN pip install flake8 pytest

RUN cd rai-python && \
    git log -1