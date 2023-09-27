### Generate Local Database

When the app runs locally it is configured to use the database configuration defined in the `.env` file. The configuration should be a local database so the production database is not affected during development.

First, install [MySQL](https://dev.mysql.com/downloads/). You will need the community server as well as a MySQL client. MySQL Workbench (GUI) is optional. The installation process for a MySQL client varies depending on your operating system (see below). For Windows, use the MySQL Installer for Windows. Note that the MySQL shell is different and will not work for the following backup and restore commands.

```
# MySQL Client
# Mac (Homebrew)
brew install mysql-client

# Linux (yum)
yum install mysql

#How To get Yum On WSL
sudo apt update -y
sudo apt install -y yum-utils
```