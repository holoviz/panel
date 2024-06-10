# AWS: Amazon Web Services

The following guide demonstrates how to deploy a Panel app on an AWS EC2 instance.

## 1. Set up an EC2 instance with your selected AMI

To get started, AWS EC2 has a free tier with Linux and Windows t2/t3.micro instances.

## 2. Configure Security Groups

Security groups define who/which IP addresses can request and receive data from your instance. The first "rule" attached to Port 22 defines which IP's can ssh into your instance.

The second rule which we will add, configures the port that Panel will serve the app on.

- Under *Configure Security Group*, add a rule with the following:
  - Type: Custom TCP Rule
  - Port Range: 5006
  - Source*: MyIP

:::{note}
On final deployment, setting ssh's Source to *MyIP* and panel's port Source to *Anywhere* could be the set-up for a publicly available site, though there are other security considerations here.
:::

## 3. Launch and connect to instance

Create and change modifications as needed to a keypair file.

```bash
$ chmod 400 <filename>.pem
$ ssh -i "<filename>.pem" ubuntu@<Public DNS>
```

Your instance's Public DNS is the domain name associated with the Public IPv4 address assigned to your instance. Note that this changes every time you stop/start your instance.

- Public IP address format: `x.x.x.x`, where x represents 32 or 128 bit numbers.
- Public DNS format: `ec2-x-x-x-x.us-east-2.compute.amazonaws.com`.

## 4. Install dependencies & requirements

Once connected, run the following to manage Python package dependencies and requirements. Depending on your app, you may have to install other applications and dependencies.

```bash
$ sudo apt-get update
$ sudo apt-get install -y python3-pip
```

## 5. Transfer code to instance

In the terminal you just ssh'd into, find a way to transfer the code to your instance. This can either be via cloning a git repo or scp'ing files/directories from your local drive. Install any additional requirements.

```bash
$ git clone <repo-link>
$ pip install -r requirements.txt

# Alternatively, scp files/directories from your local machine:
$ scp -i <keypair-name>.pem <file> <Public DNS>:</path-to-destination/>
$ scp -i <keypair-name>.pem -r <directory> <Public DNS>:</path-to-destination/>
```

## 6. Serve app

Assuming `app.py` returns a `xyz.servable()` panel object, the command below serves your app on the specified port.

```bash
$ python3 -m panel serve app.py --address 0.0.0.0 --port 5006 --allow-websocket-origin=<Public IPv4>:5006
```

```bash
The app can be viewed in your browser:

    URL: http://x.x.x.x:5006/

where x.x.x.x is your instance's Public IP address.
```

## Other deployment notes

- Using `nohup` for final deploy: This keeps your session running even when you disconnect from your session.
- You can register for a SSL certificate & set up a reverse proxy using NGINX or Apache. There may be further specifications to AWS security groups.
