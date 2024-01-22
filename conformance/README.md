# AV1 Codec ISO Media File Format Binding Conformance Report

## :warning: **WARNING** :warning:

Files in this folder are still under review by other members of the group.

## Installing LFS for the first time

If you don't have git LFS installed on your system you will need to install it in order to download the files when you clone the repository.
Run `git lfs version` command to see if you have LFS installed on your system.
If you don't have it installed you can do the following:

1. Install Git LFS: Visit the [Git LFS website](https://git-lfs.github.com/) and follow the installation instructions for your operating system.  
E.g.: On macOS you can run: `brew install git-lfs`

2. Once Git LFS is installed, you should set it up for use with your repositories. In your terminal, run: `git lfs install`  
This command sets up Git LFS hooks and filters for the repository.

3. Now you're ready to clone a repository: `git clone https://github.com/AOMediaCodec/av1-isobmff.git`

4. At this point, Git LFS should have downloaded all LFS files in the repository. You can confirm this by checking the size of the LFS files in your local repository. They should match the size of the files in the remote repository. In some cases, Git LFS files might not download automatically when you clone a repository. If this happens, you can manually download the LFS files with the `git lfs pull` command. Run this command in the root directory of your local repository to download all Git LFS files: `git lfs pull`

## Adding new files to conformance suite

At the moment we don't run automatic metadata extraction on the files that are contributed. This will be done in the future version of the software but currently if you want to contribute files you have to follow the following steps. 

Let's assume you have files sored in the local folder named `./MyCompany` and you want to contribute the files inside that directory.
If you have a license associated with your files, you can provide it in a form of a text file e.g. `licence.txt`. The contents of this file will be copied to every metadata json file for each file in `./MyCompany` directory.

Follow these steps to contribute new files:

1. Make sure you have python poetry installed. Follow the [installation guidelines](https://python-poetry.org/docs/#installation) for your OS.
2. Make sure you have [Compliance Warden](https://github.com/gpac/ComplianceWarden) installed on your OS. Look for `./bin/cw.exe`.
2. Go to conformance direcory and install dependencies:  
    ```sh
    cd conformance
    poetry install
    ```
3. Run the following command to add your files to the conformance suite:    
    ```sh
    poetry run manage-files -i MyCompany -l licence.txt -e path/to/bin/cw.exe
    ```
    With `path/to/bin/cw.exe` being a path to the Compliance Warden executable which you compiled in step 2.

This script will ask you a couple of questions for each file and will run the `cw.exe` on every file found in `./MyCompany` directory.
It will then copy your conformance files to the `conformance/conformance_files` directory with all the metadata associated to it.
After that you can open a new pull request to the repository.
